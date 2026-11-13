"""Tela Início: recomendação de treino do dia gerada por IA a partir dos registros do usuário."""

import logging
import time
from datetime import date
from typing import Any

import reflex as rx

from projetofacul.logic.navegacao import ROTA_LOGIN
from projetofacul.logic.recomendacao import (
    ESQUEMA_RESPOSTA,
    INSTRUCAO_SISTEMA,
    MAXIMO_TOKENS_RECOMENDACAO,
    build_recommendation_context,
    build_recommendation_payload,
    build_recommendation_prompt,
    build_recommendation_view,
    get_recommendation_failure_message,
    has_recent_records,
    parse_iso_date,
    parse_recommendation,
)
from projetofacul.logic.sono_registro import FUSO_BRASILIA_OFFSET_MINUTOS
from projetofacul.services import gemini_client, xano_client
from projetofacul.services.gemini_client import GeminiError
from projetofacul.services.xano_client import XanoError
from projetofacul.states.sessao_state import SessaoState

logger = logging.getLogger(__name__)

# data e fuso vêm do navegador: o servidor do Reflex pode estar em outro fuso
SCRIPT_RELOGIO = (
    "(() => { const d = new Date(); const p = (n) => String(n).padStart(2, '0');"
    " return {hoje: `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`,"
    " offset_minutos: d.getTimezoneOffset()}; })()"
)

ESTADO_PREPARANDO = "preparando"
ESTADO_PRONTA = "pronta"
ESTADO_SEM_DADOS = "sem_dados"
ESTADO_ERRO = "erro"

SESSAO_EXPIRADA = "sessao_expirada"
SEM_DADOS = "sem_dados"


def get_now_ms() -> int:
    # horário exibido quando a recomendação não pôde ser guardada; substituível nos testes
    return int(time.time() * 1000)


def read_offset(valor: Any) -> int:
    try:
        offset = int(valor)
    except (TypeError, ValueError):
        return FUSO_BRASILIA_OFFSET_MINUTOS
    # fusos reais vão de UTC−12 a UTC+14
    return offset if -14 * 60 <= offset <= 12 * 60 else FUSO_BRASILIA_OFFSET_MINUTOS


def get_missing_configuration() -> list[str]:
    """Nomes (nunca valores) do que falta no ambiente do servidor para gerar e guardar."""
    faltando = []
    if not gemini_client.is_configured():
        faltando.append("GEMINI_API_KEY")
    if not xano_client.has_analysis_secret():
        faltando.append("PULSE_ANALISE_SECRET")
    return faltando


async def generate_for_user(
    token: str, perfil: dict[str, Any], hoje: date, offset_minutos: int
) -> tuple[dict[str, Any] | None, str]:
    """Busca os registros, pede a recomendação à IA e tenta guardá-la.

    Devolve (registro para exibir, "") ou (None, tipo da falha). Roda fora do lock do State.
    """
    try:
        sonos = await xano_client.list_sono(token)
        refeicoes = await xano_client.list_refeicoes(token)
        treinos = await xano_client.list_treinos(token)
    except XanoError as erro:
        return None, SESSAO_EXPIRADA if erro.tipo == "nao_autorizado" else "registros"

    contexto = build_recommendation_context(perfil, sonos, refeicoes, treinos, hoje, offset_minutos)
    if not has_recent_records(contexto):
        return None, SEM_DADOS

    faltando = get_missing_configuration()
    if faltando:
        logger.warning(
            "Recomendação do dia desativada: defina %s no .env e reinicie o reflex run", " e ".join(faltando)
        )
        return None, "nao_configurado"

    try:
        resposta = await gemini_client.generate_json(
            INSTRUCAO_SISTEMA,
            build_recommendation_prompt(contexto),
            ESQUEMA_RESPOSTA,
            "recomendação do dia",
            MAXIMO_TOKENS_RECOMENDACAO,
        )
    except GeminiError as erro:
        return None, erro.tipo

    resultado = parse_recommendation(resposta)
    if resultado.status != "valida":
        logger.warning("Resposta da IA fora do formato esperado (recomendação do dia)")
        return None, "falha"

    payload = build_recommendation_payload(resultado.valores, hoje, gemini_client.get_model())
    try:
        gravada = await xano_client.save_recommendation(token, payload)
    except XanoError as erro:
        if erro.tipo == "nao_autorizado":
            return None, SESSAO_EXPIRADA
        # a recomendação é válida: aparece mesmo sem ser guardada; a próxima visita gera outra
        logger.warning("Recomendação do dia exibida sem ser guardada (%s)", erro.tipo)
        gravada = {}
    return {"created_at": get_now_ms(), **payload, **gravada}, ""


class InicioState(rx.State):
    """Card "Recomendação de hoje": busca a do dia, gera quando falta e atende ao "Atualizar"."""

    estado: str = ESTADO_PREPARANDO
    recomendacao: dict[str, str] = {}
    mensagem_erro: str = ""
    atualizando: bool = False

    # só no servidor: dia e fuso do navegador e trava contra gerações em paralelo
    _hoje: str = ""
    _offset_minutos: int = FUSO_BRASILIA_OFFSET_MINUTOS
    _gerando: bool = False

    def get_today(self) -> date:
        return parse_iso_date(self._hoje) or date.today()

    def apply_clock(self, relogio: dict):
        self._hoje = str((relogio or {}).get("hoje") or "")
        self._offset_minutos = read_offset((relogio or {}).get("offset_minutos"))

    def show_failure(self, tipo: str):
        self.mensagem_erro = get_recommendation_failure_message(tipo)
        # com uma recomendação na tela (falha no "Atualizar"), ela continua visível
        if self.estado != ESTADO_PRONTA:
            self.estado = ESTADO_ERRO

    def start_generation(self):
        """Liga a trava e devolve o evento de geração; None se já houver uma em andamento."""
        # eventos do mesmo usuário rodam em fila: o segundo clique já encontra a trava ligada
        if self._gerando:
            return None
        self._gerando = True
        self.mensagem_erro = ""
        if self.estado == ESTADO_PRONTA:
            self.atualizando = True
        else:
            self.estado = ESTADO_PREPARANDO
        return InicioState.generate_recommendation

    @rx.event
    async def start_page(self):
        """on_load de /inicio (depois do guarda de sessão) e botão "Tentar novamente"."""
        sessao = await self.get_state(SessaoState)
        if not sessao.sessao_verificada:
            return
        self.estado = ESTADO_PREPARANDO
        self.mensagem_erro = ""
        return rx.call_script(SCRIPT_RELOGIO, callback=InicioState.load_recommendation)

    @rx.event
    async def load_recommendation(self, relogio: dict):
        self.apply_clock(relogio)
        sessao = await self.get_state(SessaoState)
        if not sessao.sessao_verificada:
            return
        try:
            registro = await xano_client.get_today_recommendation(sessao.token, self.get_today().isoformat())
        except XanoError as erro:
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                return rx.redirect(ROTA_LOGIN)
            self.show_failure("registros")
            return
        if registro:
            # a do dia já existe (outra visita ou outro aparelho): nada de IA
            self.recomendacao = build_recommendation_view(registro, self._offset_minutos)
            self.estado = ESTADO_PRONTA
            return
        return self.start_generation()

    @rx.event
    def refresh_recommendation(self):
        """Botão "Atualizar": relê o relógio (a página pode ter virado o dia) e gera de novo."""
        if self._gerando:
            return
        self.atualizando = True
        return rx.call_script(SCRIPT_RELOGIO, callback=InicioState.generate_with_clock)

    @rx.event
    def generate_with_clock(self, relogio: dict):
        self.apply_clock(relogio)
        return self.start_generation()

    @rx.event(background=True)
    async def generate_recommendation(self):
        """Gera sem segurar o State durante as chamadas ao Xano e à IA."""
        async with self:
            if not self._gerando:
                return
            sessao = await self.get_state(SessaoState)
            token = sessao.token
            perfil = dict(sessao._perfil or {})
            hoje = self.get_today()
            offset = self._offset_minutos

        registro, falha = await generate_for_user(token, perfil, hoje, offset)

        async with self:
            self._gerando = False
            self.atualizando = False
            if falha == SESSAO_EXPIRADA:
                sessao = await self.get_state(SessaoState)
                sessao.clear_session()
                return rx.redirect(ROTA_LOGIN)
            if falha == SEM_DADOS:
                self.recomendacao = {}
                self.mensagem_erro = ""
                self.estado = ESTADO_SEM_DADOS
            elif falha:
                self.show_failure(falha)
            else:
                self.recomendacao = build_recommendation_view(registro, offset)
                self.mensagem_erro = ""
                self.estado = ESTADO_PRONTA
