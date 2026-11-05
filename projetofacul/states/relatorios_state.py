"""Tela de Relatórios: carrega os registros do usuário e monta as séries dos gráficos."""

from typing import Any

import reflex as rx

from projetofacul.logic.navegacao import ROTA_LOGIN
from projetofacul.logic.relatorios import (
    RELATORIOS,
    TIPOS_GRAFICO,
    build_report_points,
    has_enough_data,
    normalize_chart_type,
)
from projetofacul.logic.treinos import get_today_sao_paulo
from projetofacul.services import xano_client
from projetofacul.services.xano_client import XanoError, get_failure_message
from projetofacul.states.sessao_state import SessaoState

# relatório -> função de listagem do xano_client (pelo nome, para os testes simularem)
FUNCOES_LISTAGEM = {
    "treinos": "list_treinos",
    "sono": "list_sono",
    "peso": "list_registros_peso",
    "calorias": "list_refeicoes",
}

MENSAGENS_FALHA = {
    "treinos": "Não foi possível carregar seus treinos agora.",
    "sono": "Não foi possível carregar seus registros de sono agora.",
    "peso": "Não foi possível carregar seus registros de peso agora.",
    "calorias": "Não foi possível carregar suas refeições agora.",
}


class RelatoriosState(rx.State):
    """Séries prontas por relatório, erros por card e tipo de gráfico escolhido."""

    carregando: bool = True

    pontos_treinos: list[dict[str, Any]] = []
    pontos_sono: list[dict[str, Any]] = []
    pontos_peso: list[dict[str, Any]] = []
    pontos_calorias: list[dict[str, Any]] = []

    suficiente_treinos: bool = False
    suficiente_sono: bool = False
    suficiente_peso: bool = False
    suficiente_calorias: bool = False

    erro_treinos: str = ""
    erro_sono: str = ""
    erro_peso: str = ""
    erro_calorias: str = ""

    # preferência de gráfico por relatório, só no navegador (nunca vai ao Xano)
    grafico_treinos: str = rx.LocalStorage("", name="pulse_grafico_treinos")
    grafico_sono: str = rx.LocalStorage("", name="pulse_grafico_sono")
    grafico_peso: str = rx.LocalStorage("", name="pulse_grafico_peso")
    grafico_calorias: str = rx.LocalStorage("", name="pulse_grafico_calorias")

    @rx.var
    def tipo_treinos(self) -> str:
        return normalize_chart_type(self.grafico_treinos, "treinos")

    @rx.var
    def tipo_sono(self) -> str:
        return normalize_chart_type(self.grafico_sono, "sono")

    @rx.var
    def tipo_peso(self) -> str:
        return normalize_chart_type(self.grafico_peso, "peso")

    @rx.var
    def tipo_calorias(self) -> str:
        return normalize_chart_type(self.grafico_calorias, "calorias")

    def set_report(self, relatorio: str, pontos: list[dict[str, Any]], erro: str):
        setattr(self, f"pontos_{relatorio}", pontos)
        setattr(self, f"suficiente_{relatorio}", has_enough_data(relatorio, pontos))
        setattr(self, f"erro_{relatorio}", erro)

    @rx.event
    async def start_page(self):
        """on_load de /relatorios (depois do guarda de sessão) e botão "Tentar novamente"."""
        sessao = await self.get_state(SessaoState)
        # o guarda já redirecionou (sem login ou onboarding pendente): nada a carregar aqui
        if not sessao.sessao_verificada:
            return
        self.carregando = True
        yield

        hoje = get_today_sao_paulo()
        # em sequência, não em paralelo: o plano gratuito do Xano limita rajadas
        for relatorio in RELATORIOS:
            listar = getattr(xano_client, FUNCOES_LISTAGEM[relatorio])
            try:
                registros = await listar(sessao.token)
            except XanoError as erro:
                if erro.tipo == "nao_autorizado":
                    sessao.clear_session()
                    self.carregando = False
                    yield rx.redirect(ROTA_LOGIN)
                    return
                # falha só neste card; os outros continuam
                self.set_report(relatorio, [], get_failure_message(erro, MENSAGENS_FALHA[relatorio]))
                continue
            self.set_report(relatorio, build_report_points(relatorio, registros, hoje), "")

        self.carregando = False

    @rx.event
    def set_chart_type(self, relatorio: str, tipo: str):
        if relatorio not in RELATORIOS or tipo not in TIPOS_GRAFICO:
            return
        setattr(self, f"grafico_{relatorio}", tipo)
