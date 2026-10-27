"""Tela de Peso: listar, registrar e excluir pesos do usuário autenticado."""

from typing import Any

import reflex as rx

from projetofacul.logic.navegacao import ROTA_LOGIN
from projetofacul.logic.peso import (
    SEM_VALOR,
    build_registro_payload,
    build_weight_view,
    calculate_change_since_first,
    format_change,
    format_weight,
    get_current_weight,
    now_brasilia,
    sort_registros,
    validate_registro_peso,
)
from projetofacul.services import xano_client
from projetofacul.services.xano_client import XanoError, get_failure_message
from projetofacul.states.refeicoes_state import ESTILO_TOAST_SUCESSO
from projetofacul.states.sessao_state import SessaoState

MENSAGEM_FALHA_LISTAR = "Não foi possível carregar seus registros de peso agora."
MENSAGEM_FALHA_SALVAR = "Não foi possível registrar o peso agora. Tente novamente em instantes."
MENSAGEM_FALHA_EXCLUIR = "Não foi possível excluir o registro agora. Tente novamente em instantes."

CAMPOS_FORMULARIO = ("data", "horario", "peso")


class PesoState(rx.State):
    """Lista, resumo, formulário e confirmação de exclusão."""

    registros: list[dict[str, str]] = []
    carregando: bool = True
    erro_lista: str = ""
    peso_atual: str = SEM_VALOR
    variacao: str = SEM_VALOR

    hoje: str = ""
    data: str = ""
    horario: str = ""
    peso: str = ""
    erros: dict[str, str] = {}
    erro_geral: str = ""
    salvando: bool = False

    exclusao_id: str = ""
    excluindo: bool = False

    # lista crua do Xano, só no servidor (o resumo é recalculado a partir dela)
    _registros_xano: list[dict[str, Any]] = []

    def fill_date_time_now(self):
        """Data e horário padrão = agora, no horário de Brasília."""
        agora = now_brasilia()
        self.hoje = agora.strftime("%Y-%m-%d")
        self.data = self.hoje
        self.horario = agora.strftime("%H:%M")

    def update_summary(self):
        self.peso_atual = format_weight(get_current_weight(self._registros_xano))
        self.variacao = format_change(calculate_change_since_first(self._registros_xano))

    async def fetch_weights(self) -> bool:
        """Busca a lista no Xano; devolve False quando a sessão expirou."""
        sessao = await self.get_state(SessaoState)
        try:
            registros = await xano_client.list_registros_peso(sessao.token)
        except XanoError as erro:
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                return False
            self.erro_lista = get_failure_message(erro, MENSAGEM_FALHA_LISTAR)
            return True
        self._registros_xano = sort_registros(registros)
        self.registros = [build_weight_view(registro) for registro in self._registros_xano]
        self.erro_lista = ""
        self.update_summary()
        return True

    @rx.event
    async def start_page(self):
        """on_load de /peso (depois do guarda de sessão) e botão "Tentar novamente"."""
        sessao = await self.get_state(SessaoState)
        # o guarda já redirecionou (sem login ou onboarding pendente): nada a carregar aqui
        if not sessao.sessao_verificada:
            return
        self.carregando = True
        self.erro_lista = ""
        self.erro_geral = ""
        self.erros = {}
        self.fill_date_time_now()
        yield
        sessao_valida = await self.fetch_weights()
        self.carregando = False
        if not sessao_valida:
            yield rx.redirect(ROTA_LOGIN)

    @rx.event
    def update_field(self, campo: str, valor: str):
        if campo not in CAMPOS_FORMULARIO:
            return
        setattr(self, campo, "" if valor is None else str(valor))
        if campo in self.erros:
            self.erros = {chave: texto for chave, texto in self.erros.items() if chave != campo}

    @rx.event
    async def save_weight(self, _dados_formulario: dict[str, Any]):
        # os valores vêm do próprio State (inputs controlados); o dicionário do submit é ignorado
        # proteção contra duplo clique (e Enter repetido no formulário)
        if self.salvando:
            return

        dados = {campo: getattr(self, campo) for campo in CAMPOS_FORMULARIO}
        self.erros = validate_registro_peso(dados, now_brasilia())
        self.erro_geral = ""
        if self.erros:
            return

        self.salvando = True
        yield

        sessao = await self.get_state(SessaoState)
        try:
            await xano_client.create_registro_peso(sessao.token, **build_registro_payload(dados))
        except XanoError as erro:
            self.salvando = False
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                yield rx.redirect(ROTA_LOGIN)
                return
            self.erro_geral = get_failure_message(erro, MENSAGEM_FALHA_SALVAR)
            return

        self.salvando = False
        # limpa só o peso; data e horário voltam para agora
        self.peso = ""
        self.fill_date_time_now()
        await self.fetch_weights()
        yield rx.toast.success("Peso registrado", position="top-right", duration=3000, style=ESTILO_TOAST_SUCESSO)

    @rx.event
    def ask_delete(self, registro_id: str):
        self.exclusao_id = registro_id

    @rx.event
    def set_delete_open(self, aberto: bool):
        if not aberto and not self.excluindo:
            self.exclusao_id = ""

    @rx.event
    async def confirm_delete(self):
        if self.excluindo or not self.exclusao_id:
            return

        self.excluindo = True
        yield

        sessao = await self.get_state(SessaoState)
        try:
            await xano_client.delete_registro_peso(sessao.token, int(self.exclusao_id))
        except XanoError as erro:
            self.excluindo = False
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                yield rx.redirect(ROTA_LOGIN)
                return
            if erro.tipo != "nao_encontrado":
                self.exclusao_id = ""
                yield rx.toast.error(
                    get_failure_message(erro, MENSAGEM_FALHA_EXCLUIR), position="top-right", duration=4000
                )
                return
            # já não existia (ou não é do usuário): só atualiza a lista

        self.excluindo = False
        self.exclusao_id = ""
        await self.fetch_weights()
        yield rx.toast.success("Registro excluído", position="top-right", duration=3000, style=ESTILO_TOAST_SUCESSO)
