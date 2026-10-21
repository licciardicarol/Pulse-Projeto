"""Tela de Refeições: listar, registrar e excluir refeições do usuário autenticado."""

from datetime import date
from typing import Any

import reflex as rx

from projetofacul.logic.navegacao import ROTA_LOGIN
from projetofacul.logic.refeicoes import (
    build_meal_view,
    build_refeicao_payload,
    calculate_daily_totals,
    count_pending_today,
    format_number,
    parse_date,
    sort_refeicoes,
    suggest_meal_type,
    validate_refeicao,
)
from projetofacul.services import xano_client
from projetofacul.services.xano_client import MENSAGEM_LIMITE_REQUISICOES, XanoError
from projetofacul.states.sessao_state import SessaoState

MENSAGEM_FALHA_LISTAR = "Não foi possível carregar suas refeições agora."
MENSAGEM_FALHA_SALVAR = "Não foi possível registrar a refeição agora. Tente novamente em instantes."
MENSAGEM_FALHA_EXCLUIR = "Não foi possível excluir a refeição agora. Tente novamente em instantes."

# data e hora vêm do navegador: o servidor do Reflex pode estar em outro fuso
SCRIPT_RELOGIO = (
    "(() => { const d = new Date(); const p = (n) => String(n).padStart(2, '0');"
    " return {hoje: `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`, hora: d.getHours()}; })()"
)

CAMPOS_FORMULARIO = ("data_refeicao", "tipo", "descricao")

# toast verde de sucesso, no padrão escuro do app (canto superior direito, ~3s)
ESTILO_TOAST_SUCESSO = {"background": "#0F2A22", "border": "1px solid rgba(52,211,153,.45)", "color": "#D1FAE5"}


def get_failure_message(erro: XanoError, mensagem_padrao: str) -> str:
    # o limite do Xano tem mensagem própria: basta esperar alguns segundos
    return MENSAGEM_LIMITE_REQUISICOES if erro.tipo == "limite_requisicoes" else mensagem_padrao


class RefeicoesState(rx.State):
    """Lista, totais do dia, formulário do modal e confirmação de exclusão."""

    refeicoes: list[dict[str, str]] = []
    carregando: bool = True
    erro_lista: str = ""
    hoje: str = ""
    total_calorias: str = "0"
    total_proteinas: str = "0"
    total_carboidratos: str = "0"
    total_gorduras: str = "0"
    pendentes_hoje: int = 0

    modal_aberto: bool = False
    data_refeicao: str = ""
    tipo: str = ""
    descricao: str = ""
    erros: dict[str, str] = {}
    erro_geral: str = ""
    salvando: bool = False

    exclusao_id: str = ""
    excluindo: bool = False

    # lista crua do Xano, só no servidor (os totais são recalculados a partir dela)
    _refeicoes_xano: list[dict[str, Any]] = []

    def get_today(self) -> date:
        return parse_date(self.hoje) or date.today()

    def update_totals(self):
        hoje = self.get_today()
        totais = calculate_daily_totals(self._refeicoes_xano, hoje)
        self.total_calorias = format_number(totais["calorias"])
        self.total_proteinas = format_number(totais["proteinas"])
        self.total_carboidratos = format_number(totais["carboidratos"])
        self.total_gorduras = format_number(totais["gorduras"])
        self.pendentes_hoje = count_pending_today(self._refeicoes_xano, hoje)

    async def fetch_meals(self) -> bool:
        """Busca a lista no Xano; devolve False quando a sessão expirou."""
        sessao = await self.get_state(SessaoState)
        try:
            refeicoes = await xano_client.list_refeicoes(sessao.token)
        except XanoError as erro:
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                return False
            self.erro_lista = get_failure_message(erro, MENSAGEM_FALHA_LISTAR)
            return True
        self._refeicoes_xano = sort_refeicoes(refeicoes)
        self.refeicoes = [build_meal_view(refeicao) for refeicao in self._refeicoes_xano]
        self.erro_lista = ""
        self.update_totals()
        return True

    @rx.event
    async def start_page(self):
        """on_load de /refeicoes (depois do guarda de sessão) e botão "Tentar novamente"."""
        # o guarda já redirecionou (sem login ou onboarding pendente): nada a carregar aqui
        sessao = await self.get_state(SessaoState)
        if not sessao.sessao_verificada:
            return
        self.carregando = True
        self.erro_lista = ""
        return rx.call_script(SCRIPT_RELOGIO, callback=RefeicoesState.load_meals)

    @rx.event
    async def load_meals(self, relogio: dict):
        self.hoje = str(relogio.get("hoje") or "")
        sessao = await self.get_state(SessaoState)
        if not sessao.sessao_verificada:
            return
        sessao_valida = await self.fetch_meals()
        self.carregando = False
        if not sessao_valida:
            return rx.redirect(ROTA_LOGIN)

    @rx.event
    def open_new_meal(self):
        self.modal_aberto = True
        self.erro_geral = ""
        return rx.call_script(SCRIPT_RELOGIO, callback=RefeicoesState.fill_form_defaults)

    @rx.event
    def fill_form_defaults(self, relogio: dict):
        self.hoje = str(relogio.get("hoje") or self.hoje)
        # formulário novo recebe data de hoje e tipo pelo horário; um rascunho é mantido
        if not self.data_refeicao and not self.descricao:
            self.data_refeicao = self.hoje
            self.tipo = suggest_meal_type(int(relogio.get("hora") or 0))

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
        self.data_refeicao = ""
        self.tipo = ""
        self.descricao = ""
        self.erros = {}
        self.erro_geral = ""

    @rx.event
    async def save_meal(self):
        # proteção contra duplo clique
        if self.salvando:
            return

        dados = {campo: getattr(self, campo) for campo in CAMPOS_FORMULARIO}
        self.erros = validate_refeicao(dados, self.get_today())
        self.erro_geral = ""
        if self.erros:
            return

        self.salvando = True
        yield

        sessao = await self.get_state(SessaoState)
        payload = build_refeicao_payload(dados)
        try:
            await xano_client.create_refeicao(sessao.token, **payload)
        except XanoError as erro:
            self.salvando = False
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                yield rx.redirect(ROTA_LOGIN)
                return
            self.erro_geral = get_failure_message(erro, MENSAGEM_FALHA_SALVAR)
            return

        # TODO: integração futura com IA — analisar a refeição recém-criada e preencher
        # calorias, macros e `analise_ia` (capability `sugestoes`). Nada é estimado aqui.

        self.salvando = False
        self.modal_aberto = False
        self.clear_form()
        await self.fetch_meals()
        yield rx.toast.success("Refeição registrada", position="top-right", duration=3000, style=ESTILO_TOAST_SUCESSO)

    @rx.event
    def ask_delete(self, refeicao_id: str):
        self.exclusao_id = refeicao_id

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
            await xano_client.delete_refeicao(sessao.token, int(self.exclusao_id))
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
        await self.fetch_meals()
        yield rx.toast.success("Refeição excluída", position="top-right", duration=3000, style=ESTILO_TOAST_SUCESSO)
