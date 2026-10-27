"""Tela de Sono: registrar, listar, editar e excluir períodos de sono do usuário autenticado."""

from datetime import datetime, timezone
from typing import Any

import reflex as rx

from projetofacul.logic.navegacao import ROTA_LOGIN
from projetofacul.logic.sono_registro import (
    FUSO_BRASILIA_OFFSET_MINUTOS,
    TAMANHO_MAXIMO_OBSERVACOES,
    build_registro_view,
    build_sono_payload,
    calculate_duration_minutes,
    find_overlap,
    format_conflict_message,
    format_duration,
    format_input_value,
    get_form_values,
    get_local_now,
    sort_sono,
    validate_sono,
)
from projetofacul.services import xano_client
from projetofacul.services.xano_client import XanoError
from projetofacul.states.refeicoes_state import ESTILO_TOAST_SUCESSO, get_failure_message
from projetofacul.states.sessao_state import SessaoState

MENSAGEM_FALHA_LISTAR = "Não foi possível carregar seus registros de sono agora."
MENSAGEM_FALHA_SALVAR = "Não foi possível salvar o registro de sono agora."
MENSAGEM_FALHA_EXCLUIR = "Não foi possível excluir o registro de sono agora. Tente novamente em instantes."
# o app já checou a sobreposição: um "inválido" do servidor vem de um registro feito em outro dispositivo
MENSAGEM_CONFLITO_SERVIDOR = "Já existe um registro de sono nesse período. Atualize a lista e ajuste os horários."
MENSAGEM_REGISTRO_INEXISTENTE = "Esse registro de sono não existe mais. A lista foi atualizada."

# todo horário é digitado e exibido no horário de Brasília (o dia vira às 00:00 BRT)
FUSO = FUSO_BRASILIA_OFFSET_MINUTOS

CAMPOS_TEXTO = ("inicio_sono", "fim_sono", "observacoes")


def get_now() -> datetime:
    # ponto único do relógio, substituído nos testes
    return datetime.now(timezone.utc)


class SonoState(rx.State):
    """Formulário (novo ou edição), lista de registros e confirmação de exclusão."""

    registros: list[dict[str, str]] = []
    carregando: bool = True
    erro_lista: str = ""

    inicio_sono: str = ""
    fim_sono: str = ""
    qualidade_sono: int = 0
    observacoes: str = ""
    limite_maximo: str = ""
    duracao_texto: str = "—"
    pode_salvar: bool = False
    erros: dict[str, str] = {}
    erro_geral: str = ""
    erro_permite_repetir: bool = False
    salvando: bool = False
    tentou_salvar: bool = False
    editando_id: str = ""

    exclusao_id: str = ""
    excluindo: bool = False

    # lista crua do Xano, só no servidor (sobreposição, edição e ordenação usam os timestamps)
    _registros_xano: list[dict[str, Any]] = []

    def get_form_data(self) -> dict[str, Any]:
        return {
            "inicio_sono": self.inicio_sono,
            "fim_sono": self.fim_sono,
            "qualidade_sono": self.qualidade_sono,
            "observacoes": self.observacoes,
        }

    def refresh_form(self):
        """Recalcula duração, erros e o botão a cada mudança no formulário."""
        agora = get_now()
        self.limite_maximo = format_input_value(get_local_now(agora, FUSO))
        self.duracao_texto = format_duration(calculate_duration_minutes(self.inicio_sono, self.fim_sono))
        erros = validate_sono(self.get_form_data(), agora, FUSO)
        self.pode_salvar = not erros
        # campo ainda não preenchido já desabilita o botão; "obrigatório" só aparece depois de tentar salvar
        if not self.tentou_salvar:
            for campo in ("inicio_sono", "fim_sono", "qualidade_sono"):
                if not getattr(self, campo):
                    erros.pop(campo, None)
        self.erros = erros

    def reset_form(self):
        # data e hora livres: o formulário começa vazio
        self.inicio_sono = ""
        self.fim_sono = ""
        self.qualidade_sono = 0
        self.observacoes = ""
        self.editando_id = ""
        self.tentou_salvar = False
        self.erro_geral = ""
        self.erro_permite_repetir = False
        self.refresh_form()

    def set_records(self, registros: list[dict[str, Any]]):
        self._registros_xano = sort_sono(registros)
        self.registros = [build_registro_view(registro, FUSO) for registro in self._registros_xano]

    async def fetch_records(self) -> bool:
        """Busca a lista no Xano; devolve False quando a sessão expirou."""
        sessao = await self.get_state(SessaoState)
        try:
            registros = await xano_client.list_sono(sessao.token)
        except XanoError as erro:
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                return False
            self.erro_lista = get_failure_message(erro, MENSAGEM_FALHA_LISTAR)
            return True
        self.set_records(registros)
        self.erro_lista = ""
        return True

    @rx.event
    async def start_page(self):
        """on_load de /sono (depois do guarda de sessão) e botão "Tentar novamente"."""
        # o guarda já redirecionou (sem login ou onboarding pendente): nada a carregar aqui
        sessao = await self.get_state(SessaoState)
        if not sessao.sessao_verificada:
            return
        self.carregando = True
        self.erro_lista = ""
        if not self.editando_id:
            self.reset_form()
        yield

        sessao_valida = await self.fetch_records()
        self.carregando = False
        if not sessao_valida:
            yield rx.redirect(ROTA_LOGIN)

    @rx.event
    def update_field(self, campo: str, valor: str):
        if campo not in CAMPOS_TEXTO:
            return
        if campo == "observacoes":
            valor = valor[:TAMANHO_MAXIMO_OBSERVACOES]
        setattr(self, campo, valor)
        self.erro_geral = ""
        self.refresh_form()

    @rx.event
    def select_qualidade(self, qualidade: int):
        self.qualidade_sono = int(qualidade)
        self.erro_geral = ""
        self.refresh_form()

    def show_save_error(self, mensagem: str, permite_repetir: bool):
        self.erro_geral = mensagem
        self.erro_permite_repetir = permite_repetir

    @rx.event
    async def save_sono(self):
        # proteção contra duplo clique
        if self.salvando:
            return

        self.tentou_salvar = True
        self.erro_geral = ""
        self.refresh_form()
        if not self.pode_salvar:
            return

        dados = self.get_form_data()
        payload = build_sono_payload(dados, FUSO)
        conflito = find_overlap(payload["inicio_sono"], payload["fim_sono"], self._registros_xano, self.editando_id)
        if conflito:
            self.show_save_error(format_conflict_message(conflito, FUSO), False)
            return

        self.salvando = True
        yield

        sessao = await self.get_state(SessaoState)
        editando_id = self.editando_id
        try:
            if editando_id:
                registro = await xano_client.update_sono(sessao.token, int(editando_id), **payload)
            else:
                registro = await xano_client.create_sono(sessao.token, **payload)
        except XanoError as erro:
            self.salvando = False
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                yield rx.redirect(ROTA_LOGIN)
                return
            if erro.tipo == "invalido":
                self.show_save_error(MENSAGEM_CONFLITO_SERVIDOR, False)
                await self.fetch_records()
                return
            if erro.tipo == "nao_encontrado" and editando_id:
                await self.fetch_records()
                self.reset_form()
                self.show_save_error(MENSAGEM_REGISTRO_INEXISTENTE, False)
                return
            self.show_save_error(get_failure_message(erro, MENSAGEM_FALHA_SALVAR), True)
            return

        # insere/atualiza com a resposta do servidor, sem gastar outra requisição
        if isinstance(registro, dict) and registro.get("id") is not None:
            outros = [r for r in self._registros_xano if str(r.get("id", "")) != str(registro["id"])]
            self.set_records([registro, *outros])
        else:
            await self.fetch_records()

        self.salvando = False
        self.reset_form()
        mensagem = "Registro de sono atualizado" if editando_id else "Sono registrado com sucesso"
        yield rx.toast.success(mensagem, position="top-right", duration=3000, style=ESTILO_TOAST_SUCESSO)

    @rx.event
    def start_edit(self, registro_id: str):
        registro = next((r for r in self._registros_xano if str(r.get("id", "")) == registro_id), None)
        if registro is None or self.salvando:
            return
        valores = get_form_values(registro, FUSO)
        self.inicio_sono = valores["inicio_sono"]
        self.fim_sono = valores["fim_sono"]
        self.qualidade_sono = valores["qualidade_sono"]
        self.observacoes = valores["observacoes"]
        self.editando_id = registro_id
        self.tentou_salvar = False
        self.erro_geral = ""
        self.erro_permite_repetir = False
        self.refresh_form()
        return rx.scroll_to("sono-formulario")

    @rx.event
    def cancel_edit(self):
        if not self.salvando:
            self.reset_form()

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
        registro_id = self.exclusao_id
        try:
            await xano_client.delete_sono(sessao.token, int(registro_id))
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
            # já não existia (ou não é do usuário): só tira da lista

        self.excluindo = False
        self.exclusao_id = ""
        self.set_records([r for r in self._registros_xano if str(r.get("id", "")) != registro_id])
        if self.editando_id == registro_id:
            self.reset_form()
        yield rx.toast.success("Registro de sono excluído", position="top-right", duration=3000, style=ESTILO_TOAST_SUCESSO)
