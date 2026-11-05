"""Séries dos Relatórios, calculadas só com os registros do usuário.

Sem Reflex e sem rede. Cada função devolve pontos em ordem cronológica no
formato `{"rotulo": "dd/mm", "valor": float | None, "texto": "..."}`; `valor`
None é lacuna no gráfico (nunca zero). Datas no fuso de Brasília.
"""

from datetime import date, timedelta
from typing import Any

from projetofacul.logic.peso import (
    SEM_VALOR,
    format_weight,
    from_milliseconds,
    get_created_at,
    get_timestamp,
    get_weight,
)
from projetofacul.logic.refeicoes import get_number, is_analyzed
from projetofacul.logic.sono_registro import (
    FUSO_BRASILIA_OFFSET_MINUTOS,
    from_utc_ms,
    get_duration_minutes,
    get_period_ms,
    sort_sono,
)
from projetofacul.logic.treinos import parse_date

RELATORIOS = ("treinos", "sono", "peso", "calorias")
TIPOS_GRAFICO = ("colunas", "linhas")
GRAFICO_PADRAO = {"treinos": "colunas", "sono": "colunas", "peso": "linhas", "calorias": "colunas"}

SEMANAS_TREINOS = 8
REGISTROS_SONO = 30
DIAS_CALORIAS = 14
MINIMO_PESOS = 2


def format_label(dia: date) -> str:
    return dia.strftime("%d/%m")


def format_thousands(valor: float) -> str:
    """1850.4 -> "1.850" (inteiro, separador de milhar brasileiro)."""
    return f"{round(valor):,}".replace(",", ".")


def build_point(rotulo: str, valor: float | None, texto: str) -> dict[str, Any]:
    return {"rotulo": rotulo, "valor": valor, "texto": texto}


def build_weekly_workouts(treinos: list[dict[str, Any]], hoje: date) -> list[dict[str, Any]]:
    """Treinos por semana (segunda a domingo), nas últimas 8 semanas até hoje."""
    segunda_atual = hoje - timedelta(days=hoje.weekday())
    segundas = [segunda_atual - timedelta(weeks=atras) for atras in range(SEMANAS_TREINOS - 1, -1, -1)]
    contagem = dict.fromkeys(segundas, 0)

    for treino in treinos:
        dia = parse_date(str(treino.get("data") or ""))
        # fora da janela ou no futuro não conta
        if dia is None or not segundas[0] <= dia <= hoje:
            continue
        contagem[dia - timedelta(days=dia.weekday())] += 1

    return [
        build_point(format_label(segunda), quantidade, f"{quantidade} treino{'' if quantidade == 1 else 's'}")
        for segunda, quantidade in contagem.items()
    ]


def build_sleep_hours(
    registros: list[dict[str, Any]],
    quantidade: int = REGISTROS_SONO,
    offset_minutos: int = FUSO_BRASILIA_OFFSET_MINUTOS,
) -> list[dict[str, Any]]:
    """Horas das últimas `quantidade` noites com duração válida, da mais antiga à mais nova."""
    noites = []
    for registro in sort_sono(registros):
        minutos = get_duration_minutes(registro)
        if not minutos:
            continue
        periodo = get_period_ms(registro)
        # rótulo = dia em que a pessoa acordou (mesmo critério do resumo de sono)
        acordou = from_utc_ms(periodo[1], offset_minutos) if periodo else None
        horas = round(minutos / 60, 1)
        rotulo = format_label(acordou.date()) if acordou else ""
        noites.append(build_point(rotulo, horas, f"{horas:.1f} h".replace(".", ",")))
        if len(noites) == quantidade:
            break
    return list(reversed(noites))


def build_weight_evolution(registros: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Peso de cada registro válido, em ordem cronológica da pesagem."""
    ordenados = sorted(registros, key=lambda registro: (get_timestamp(registro), get_created_at(registro)))
    pontos = []
    for registro in ordenados:
        peso = get_weight(registro)
        momento = from_milliseconds(registro.get("data_horario"))
        if peso is None or peso <= 0 or momento is None:
            continue
        pontos.append(build_point(format_label(momento.date()), round(peso, 2), format_weight(peso)))
    return pontos


def build_daily_calories(refeicoes: list[dict[str, Any]], hoje: date) -> list[dict[str, Any]]:
    """Calorias por dia (últimos 14 dias até hoje), só de refeições analisadas pela IA."""
    dias = [hoje - timedelta(days=atras) for atras in range(DIAS_CALORIAS - 1, -1, -1)]
    totais: dict[date, float | None] = dict.fromkeys(dias)

    for refeicao in refeicoes:
        dia = parse_date(str(refeicao.get("data_refeicao") or ""))
        # o Xano devolve calorias vazias como 0: sem análise, a refeição não conta
        if dia not in totais or not is_analyzed(refeicao):
            continue
        totais[dia] = (totais[dia] or 0.0) + get_number(refeicao, "calorias")

    return [
        build_point(
            format_label(dia),
            None if total is None else round(total),
            SEM_VALOR if total is None else f"{format_thousands(total)} kcal",
        )
        for dia, total in totais.items()
    ]


def build_report_points(relatorio: str, registros: list[dict[str, Any]], hoje: date) -> list[dict[str, Any]]:
    if relatorio == "treinos":
        return build_weekly_workouts(registros, hoje)
    if relatorio == "sono":
        return build_sleep_hours(registros)
    if relatorio == "peso":
        return build_weight_evolution(registros)
    return build_daily_calories(registros, hoje)


def has_enough_data(relatorio: str, pontos: list[dict[str, Any]]) -> bool:
    if relatorio == "treinos":
        return any(ponto["valor"] for ponto in pontos)
    if relatorio == "peso":
        return len(pontos) >= MINIMO_PESOS
    if relatorio == "calorias":
        return any(ponto["valor"] is not None for ponto in pontos)
    return bool(pontos)


def normalize_chart_type(valor: str, relatorio: str) -> str:
    """Tipo salvo no navegador; vazio ou inválido volta ao padrão do relatório."""
    return valor if valor in TIPOS_GRAFICO else GRAFICO_PADRAO[relatorio]
