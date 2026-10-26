"""Regras de negócio dos treinos: data de hoje em São Paulo, validação, ordenação e exibição.

Os campos e limites espelham `xano/table/treinos.xs` e o endpoint `POST treinos/me`.
Os campos legados da tabela (`tipo`, `inicio`, `fim`, `carga`, `repeticoes`) nunca
são enviados pelo app.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any

# America/Sao_Paulo: UTC−3 fixo, sem horário de verão desde 2019 (evita instalar `tzdata` no Windows)
FUSO_SAO_PAULO = timezone(timedelta(hours=-3))

DURACAO_MINIMA = 1
DURACAO_MAXIMA = 1440
TAMANHO_MINIMO_NOME = 2
TAMANHO_MAXIMO_NOME = 60
TAMANHO_MAXIMO_CATEGORIA = 40
TAMANHO_MAXIMO_INTENSIDADE = 20
TAMANHO_MAXIMO_OBSERVACOES = 500

CAMPOS_OPCIONAIS = (
    ("categoria", TAMANHO_MAXIMO_CATEGORIA),
    ("intensidade", TAMANHO_MAXIMO_INTENSIDADE),
    ("observacoes", TAMANHO_MAXIMO_OBSERVACOES),
)


def get_today_sao_paulo(agora: datetime | None = None) -> date:
    """Dia atual em São Paulo; `agora` sem fuso é tratado como UTC."""
    agora = agora or datetime.now(timezone.utc)
    if agora.tzinfo is None:
        agora = agora.replace(tzinfo=timezone.utc)
    return agora.astimezone(FUSO_SAO_PAULO).date()


def parse_date(valor: str) -> date | None:
    try:
        return date.fromisoformat(valor.strip()[:10])
    except (AttributeError, ValueError):
        return None


def parse_duration(valor: str) -> int | None:
    """Só inteiros positivos escritos como dígitos ("60"); "60.5", "-1" e "" viram None."""
    texto = str(valor or "").strip()
    return int(texto) if texto.isdigit() else None


def validate_treino(dados: dict[str, str], hoje: date) -> dict[str, str]:
    """Devolve campo -> mensagem; dicionário vazio quando o treino pode ser salvo."""
    erros: dict[str, str] = {}

    data_treino = parse_date(dados.get("data", ""))
    if data_treino is None:
        erros["data"] = "Informe a data do treino."
    elif data_treino > hoje:
        erros["data"] = "A data não pode estar no futuro."

    duracao = parse_duration(dados.get("duracao_minutos", ""))
    if duracao is None or not DURACAO_MINIMA <= duracao <= DURACAO_MAXIMA:
        erros["duracao_minutos"] = f"Informe a duração em minutos inteiros, de {DURACAO_MINIMA} a {DURACAO_MAXIMA}."

    nome = dados.get("nome", "").strip()
    if len(nome) < TAMANHO_MINIMO_NOME:
        erros["nome"] = f"Informe o nome do treino com pelo menos {TAMANHO_MINIMO_NOME} caracteres."
    elif len(nome) > TAMANHO_MAXIMO_NOME:
        erros["nome"] = f"Use no máximo {TAMANHO_MAXIMO_NOME} caracteres."

    for campo, limite in CAMPOS_OPCIONAIS:
        if len(dados.get(campo, "").strip()) > limite:
            erros[campo] = f"Use no máximo {limite} caracteres."

    return erros


def build_treino_payload(dados: dict[str, str]) -> dict[str, Any]:
    """Só os campos da tela; opcionais vazios não são enviados e o dono vem do token."""
    payload: dict[str, Any] = {
        "data": dados["data"].strip()[:10],
        "duracao_minutos": parse_duration(dados["duracao_minutos"]),
        "nome": dados["nome"].strip(),
    }
    for campo, _ in CAMPOS_OPCIONAIS:
        valor = dados.get(campo, "").strip()
        if valor:
            payload[campo] = valor
    return payload


def sort_treinos(treinos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mais recentes primeiro: por data e, no mesmo dia, pelo id (ordem de registro)."""
    return sorted(
        treinos,
        key=lambda treino: (str(treino.get("data") or ""), int(treino.get("id") or 0)),
        reverse=True,
    )


def format_date_br(valor: str) -> str:
    data = parse_date(valor)
    return data.strftime("%d/%m/%Y") if data else ""


def build_workout_view(treino: dict[str, Any]) -> dict[str, str]:
    """Dados prontos para exibir um card (tudo texto, para o `rx.foreach`); vazio = não exibe."""
    duracao = treino.get("duracao_minutos")
    return {
        "id": str(treino.get("id", "")),
        "nome": str(treino.get("nome") or "").strip(),
        "data": format_date_br(str(treino.get("data") or "")),
        "duracao": f"{duracao} min" if isinstance(duracao, int) and duracao > 0 else "",
        "categoria": str(treino.get("categoria") or "").strip(),
        "intensidade": str(treino.get("intensidade") or "").strip(),
        "observacoes": str(treino.get("observacoes") or "").strip(),
    }
