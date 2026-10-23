"""Regras de negócio das refeições: validação, tipo sugerido, ordenação e totais do dia.

Nenhuma função aqui estima valores nutricionais: calorias e macros só existem
quando a análise por IA (integração futura) preencher `analise_ia`.
"""

from datetime import date
from typing import Any

# espelha o enum `tipo` de `xano/table/refeicoes.xs`
OPCOES_TIPO = ("Café da manhã", "Almoço", "Café da tarde", "Jantar")

TAMANHO_MINIMO_DESCRICAO = 3
TAMANHO_MAXIMO_DESCRICAO = 500

CAMPOS_NUTRICIONAIS = ("calorias", "proteinas", "carboidratos", "gorduras")


def suggest_meal_type(hora: int) -> str:
    """Tipo padrão pelo horário local: 5h–10h59, 11h–14h59, 15h–17h59, resto do dia."""
    if 5 <= hora < 11:
        return "Café da manhã"
    if 11 <= hora < 15:
        return "Almoço"
    if 15 <= hora < 18:
        return "Café da tarde"
    return "Jantar"


def parse_date(valor: str) -> date | None:
    try:
        return date.fromisoformat(valor.strip()[:10])
    except (AttributeError, ValueError):
        return None


def validate_refeicao(dados: dict[str, str], hoje: date) -> dict[str, str]:
    """Devolve campo -> mensagem; dicionário vazio quando a refeição pode ser salva."""
    erros: dict[str, str] = {}

    data_refeicao = parse_date(dados.get("data_refeicao", ""))
    if data_refeicao is None:
        erros["data_refeicao"] = "Informe a data da refeição."
    elif data_refeicao > hoje:
        erros["data_refeicao"] = "A data não pode estar no futuro."

    if dados.get("tipo", "") not in OPCOES_TIPO:
        erros["tipo"] = "Selecione o tipo da refeição."

    descricao = dados.get("descricao", "").strip()
    if len(descricao) < TAMANHO_MINIMO_DESCRICAO:
        erros["descricao"] = f"Descreva a refeição com pelo menos {TAMANHO_MINIMO_DESCRICAO} caracteres."
    elif len(descricao) > TAMANHO_MAXIMO_DESCRICAO:
        erros["descricao"] = f"Use no máximo {TAMANHO_MAXIMO_DESCRICAO} caracteres."

    return erros


def build_refeicao_payload(dados: dict[str, str]) -> dict[str, str]:
    """Só data, tipo e descrição: o app nunca envia valores nutricionais nem o dono."""
    return {
        "data_refeicao": dados["data_refeicao"].strip()[:10],
        "tipo": dados["tipo"],
        "descricao": dados["descricao"].strip(),
    }


def is_analyzed(refeicao: dict[str, Any]) -> bool:
    # o Xano devolve decimais vazios como 0; só `analise_ia` indica análise feita
    return bool(str(refeicao.get("analise_ia") or "").strip())


def sort_refeicoes(refeicoes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mais recentes primeiro: por data e, no mesmo dia, pela ordem de registro."""
    return sorted(
        refeicoes,
        key=lambda refeicao: (str(refeicao.get("data_refeicao") or ""), refeicao.get("created_at") or 0),
        reverse=True,
    )


def is_from_day(refeicao: dict[str, Any], dia: date) -> bool:
    return parse_date(str(refeicao.get("data_refeicao") or "")) == dia


def get_number(refeicao: dict[str, Any], campo: str) -> float:
    try:
        return float(refeicao.get(campo) or 0)
    except (TypeError, ValueError):
        return 0.0


def calculate_daily_totals(refeicoes: list[dict[str, Any]], hoje: date) -> dict[str, float]:
    """Soma só refeições de hoje já analisadas; sem nenhuma, tudo fica 0."""
    totais = {campo: 0.0 for campo in CAMPOS_NUTRICIONAIS}
    for refeicao in refeicoes:
        if is_from_day(refeicao, hoje) and is_analyzed(refeicao):
            for campo in CAMPOS_NUTRICIONAIS:
                totais[campo] += get_number(refeicao, campo)
    return totais


def count_pending_today(refeicoes: list[dict[str, Any]], hoje: date) -> int:
    return sum(1 for refeicao in refeicoes if is_from_day(refeicao, hoje) and not is_analyzed(refeicao))


def format_number(valor: float) -> str:
    """12.0 -> "12"; 12.5 -> "12,5" (padrão brasileiro, uma casa decimal)."""
    arredondado = round(valor, 1)
    if arredondado == int(arredondado):
        return str(int(arredondado))
    return f"{arredondado:.1f}".replace(".", ",")


def format_date_br(valor: str) -> str:
    data = parse_date(valor)
    return data.strftime("%d/%m/%Y") if data else ""


def build_meal_view(refeicao: dict[str, Any]) -> dict[str, str]:
    """Dados prontos para exibir um item da lista (tudo texto, para o `rx.foreach`)."""
    analisada = is_analyzed(refeicao)
    macros = ""
    if analisada:
        macros = (
            f"Proteínas {format_number(get_number(refeicao, 'proteinas'))} g · "
            f"Carboidratos {format_number(get_number(refeicao, 'carboidratos'))} g · "
            f"Gorduras {format_number(get_number(refeicao, 'gorduras'))} g"
        )
    return {
        "id": str(refeicao.get("id", "")),
        "tipo": str(refeicao.get("tipo") or "Sem tipo"),
        "data": format_date_br(str(refeicao.get("data_refeicao") or "")),
        "descricao": str(refeicao.get("descricao") or ""),
        "analisada": "sim" if analisada else "",
        "calorias": f"{format_number(get_number(refeicao, 'calorias'))} kcal" if analisada else "",
        "macros": macros,
    }
