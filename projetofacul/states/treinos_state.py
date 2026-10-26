"""Tela de Treinos: listar, registrar e excluir treinos do usuário autenticado."""

from typing import Any

import reflex as rx

from projetofacul.logic.navegacao import ROTA_LOGIN
from projetofacul.logic.treinos import (
    build_treino_payload,
    build_workout_view,
    get_today_sao_paulo,
    sort_treinos,
    validate_treino,
)
from projetofacul.services import xano_client
from projetofacul.services.xano_client import MENSAGEM_LIMITE_REQUISICOES, XanoError
from projetofacul.states.sessao_state import SessaoState

MENSAGEM_FALHA_LISTAR = "Não foi possível carregar seus treinos agora."
MENSAGEM_FALHA_SALVAR = "Não foi possível registrar o treino agora. Tente novamente em instantes."
MENSAGEM_FALHA_EXCLUIR = "Não foi possível excluir o treino agora. Tente novamente em instantes."

CAMPOS_FORMULARIO = ("data", "duracao_minutos", "nome", "categoria", "intensidade", "observacoes")

# toast verde de sucesso, no padrão escuro do app (canto superior direito, ~3s)
ESTILO_TOAST_SUCESSO = {"background": "#0F2A22", "border": "1px solid rgba(52,211,153,.45)", "color": "#D1FAE5"}


def get_failure_message(erro: XanoError, mensagem_padrao: str) -> str:
    # o limite do Xano tem mensagem própria: basta esperar alguns segundos
    return MENSAGEM_LIMITE_REQUISICOES if erro.tipo == "limite_requisicoes" else mensagem_padrao


class TreinosState(rx.State):
    """Lista, formulário do modal e confirmação de exclusão."""

    treinos: list[dict[str, str]] = []
    carregando: bool = True
    erro_lista: str = ""
    # "hoje" sempre em America/Sao_Paulo, calculado no servidor (independe do fuso do navegador)
    hoje: str = ""

    modal_aberto: bool = False
    data: str = ""
    duracao_minutos: str = ""
    nome: str = ""
    categoria: str = ""
    intensidade: str = ""
    observacoes: str = ""
    erros: dict[str, str] = {}
    erro_geral: str = ""
    salvando: bool = False

    exclusao_id: str = ""
    exclusao_nome: str = ""
    excluindo: bool = False

    def refresh_today(self):
        self.hoje = get_today_sao_paulo().isoformat()

    async def fetch_workouts(self) -> bool:
        """Busca a lista no Xano; devolve False quando a sessão expirou."""
        sessao = await self.get_state(SessaoState)
        try:
            treinos: list[dict[str, Any]] = await xano_client.list_treinos(sessao.token)
        except XanoError as erro:
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                return False
            self.erro_lista = get_failure_message(erro, MENSAGEM_FALHA_LISTAR)
            return True
        self.treinos = [build_workout_view(treino) for treino in sort_treinos(treinos)]
        self.erro_lista = ""
        return True

    @rx.event
    async def start_page(self):
        """on_load de /treinos (depois do guarda de sessão) e botão "Tentar novamente"."""
        # o guarda já redirecionou (sem login ou onboarding pendente): nada a carregar aqui
        sessao = await self.get_state(SessaoState)
        if not sessao.sessao_verificada:
            return
        self.refresh_today()
        self.carregando = True
        self.erro_lista = ""
        yield
        sessao_valida = await self.fetch_workouts()
        self.carregando = False
        if not sessao_valida:
            yield rx.redirect(ROTA_LOGIN)

    @rx.event
    def open_new_workout(self):
        self.refresh_today()
        self.modal_aberto = True
        self.erro_geral = ""
        # formulário novo recebe a data de hoje (SP); um rascunho é mantido
        if not any(getattr(self, campo) for campo in CAMPOS_FORMULARIO):
            self.data = self.hoje

    @rx.event
    def set_modal_open(self, aberto: bool):
        # fechar por X, Esc ou clique fora mantém o que foi digitado
        if not self.salvando:
            self.modal_aberto = aberto

    @rx.event
    def update_field(self, campo: str, valor: str):
        if campo not in CAMPOS_FORMULARIO:
            return
        setattr(self, campo, valor)
        if campo in self.erros:
            self.erros = {chave: texto for chave, texto in self.erros.items() if chave != campo}

    def clear_form(self):
        for campo in CAMPOS_FORMULARIO:
            setattr(self, campo, "")
        self.erros = {}
        self.erro_geral = ""

    @rx.event
    async def save_workout(self):
        # proteção contra duplo clique
        if self.salvando:
            return

        self.refresh_today()
        dados = {campo: getattr(self, campo) for campo in CAMPOS_FORMULARIO}
        self.erros = validate_treino(dados, get_today_sao_paulo())
        self.erro_geral = ""
        if self.erros:
            return

        self.salvando = True
        yield

        sessao = await self.get_state(SessaoState)
        try:
            await xano_client.create_treino(sessao.token, build_treino_payload(dados))
        except XanoError as erro:
            self.salvando = False
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                yield rx.redirect(ROTA_LOGIN)
                return
            self.erro_geral = get_failure_message(erro, MENSAGEM_FALHA_SALVAR)
            return

        self.salvando = False
        self.modal_aberto = False
        self.clear_form()
        await self.fetch_workouts()
        yield rx.toast.success("Treino registrado", position="top-right", duration=3000, style=ESTILO_TOAST_SUCESSO)

    @rx.event
    def ask_delete(self, treino_id: str, nome: str):
        self.exclusao_id = treino_id
        self.exclusao_nome = nome

    @rx.event
    def set_delete_open(self, aberto: bool):
        if not aberto and not self.excluindo:
            self.exclusao_id = ""
            self.exclusao_nome = ""

    @rx.event
    async def confirm_delete(self):
        if self.excluindo or not self.exclusao_id:
            return

        self.excluindo = True
        yield

        sessao = await self.get_state(SessaoState)
        try:
            await xano_client.delete_treino(sessao.token, int(self.exclusao_id))
        except XanoError as erro:
            self.excluindo = False
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                yield rx.redirect(ROTA_LOGIN)
                return
            if erro.tipo != "nao_encontrado":
                self.exclusao_id = ""
                self.exclusao_nome = ""
                yield rx.toast.error(
                    get_failure_message(erro, MENSAGEM_FALHA_EXCLUIR), position="top-right", duration=4000
                )
                return
            # já não existia (ou não é do usuário): só atualiza a lista

        self.excluindo = False
        self.exclusao_id = ""
        self.exclusao_nome = ""
        await self.fetch_workouts()
        yield rx.toast.success("Treino excluído", position="top-right", duration=3000, style=ESTILO_TOAST_SUCESSO)
