"""Regras de negócio do sono: duração, validação, sobreposição, fuso e resumo.

Horários chegam do formulário como texto no horário de Brasília
("2026-10-20T23:00", formato do `datetime-local`) e vão para o Xano em UTC
(milissegundos). O dia vira às 00:00 de Brasília para todos os usuários. O
offset segue o formato de `Date.getTimezoneOffset()` (UTC−3 → 180).

O resumo das últimas noites (`summarize_recent_sleep`) é o ponto de integração
para recomendações e Relatórios; nenhuma regra de recomendação fica aqui.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

# espelha `qualidade_sono` (int 1–5) de `xano/table/sono.xs`
OPCOES_QUALIDADE = (
    (1, "Muito ruim"),
    (2, "Ruim"),
    (3, "Regular"),
    (4, "Bom"),
    (5, "Muito bom"),
)
ROTULOS_QUALIDADE = dict(OPCOES_QUALIDADE)

DURACAO_MINIMA_MINUTOS = 15
DURACAO_MAXIMA_MINUTOS = 24 * 60
TAMANHO_MAXIMO_OBSERVACOES = 500

# Brasília (UTC−3, sem horário de verão desde 2019): referência única do dia e da hora
FUSO_BRASILIA_OFFSET_MINUTOS = 180

SEM_DURACAO = "—"


def get_timezone(offset_minutos: int) -> timezone:
    # getTimezoneOffset é positivo a oeste de UTC
    return timezone(-timedelta(minutes=offset_minutos))


def parse_local_datetime(valor: str) -> datetime | None:
    """"2026-10-20T23:00" -> datetime sem fuso; vazio ou inválido -> None."""
    try:
        texto = valor.strip()
        if not texto:
            return None
        return datetime.fromisoformat(texto).replace(second=0, microsecond=0, tzinfo=None)
    except (AttributeError, ValueError):
        return None


def format_input_value(valor: datetime) -> str:
    return valor.strftime("%Y-%m-%dT%H:%M")


def to_utc_ms(local: datetime, offset_minutos: int) -> int:
    return int(local.replace(tzinfo=get_timezone(offset_minutos)).timestamp() * 1000)


def from_utc_ms(valor: Any, offset_minutos: int) -> datetime | None:
    try:
        milissegundos = int(valor)
    except (TypeError, ValueError):
        return None
    utc = datetime.fromtimestamp(milissegundos / 1000, tz=timezone.utc)
    return utc.astimezone(get_timezone(offset_minutos)).replace(tzinfo=None)


def get_local_now(agora_utc: datetime, offset_minutos: int) -> datetime:
    return agora_utc.astimezone(get_timezone(offset_minutos)).replace(tzinfo=None, second=0, microsecond=0)


def calculate_duration_minutes(inicio: str, fim: str) -> int | None:
    """Minutos entre início e fim; None quando faltar um deles ou o fim não for depois do início."""
    inicio_local = parse_local_datetime(inicio)
    fim_local = parse_local_datetime(fim)
    if inicio_local is None or fim_local is None or fim_local <= inicio_local:
        return None
    return int((fim_local - inicio_local).total_seconds() // 60)


def format_duration(minutos: int | None) -> str:
    """480 -> "8h"; 450 -> "7h 30min"; 45 -> "45min"; None -> "—"."""
    if minutos is None or minutos <= 0:
        return SEM_DURACAO
    horas, resto = divmod(minutos, 60)
    if horas and resto:
        return f"{horas}h {resto}min"
    if horas:
        return f"{horas}h"
    return f"{resto}min"


def format_period(inicio: datetime, fim: datetime) -> str:
    """Mesmo dia: "14:00 → 14:45"; passando da meia-noite: "20/10 23:00 → 21/10 07:00"."""
    if inicio.date() == fim.date():
        return f"{inicio:%H:%M} → {fim:%H:%M}"
    return f"{inicio:%d/%m %H:%M} → {fim:%d/%m %H:%M}"


def validate_sono(dados: dict[str, Any], agora_utc: datetime, offset_minutos: int) -> dict[str, str]:
    """Devolve campo -> mensagem; dicionário vazio quando o registro pode ser salvo."""
    erros: dict[str, str] = {}

    inicio = parse_local_datetime(str(dados.get("inicio_sono") or ""))
    fim = parse_local_datetime(str(dados.get("fim_sono") or ""))
    if inicio is None:
        erros["inicio_sono"] = "Informe o início do sono."
    if fim is None:
        erros["fim_sono"] = "Informe o fim do sono."

    if inicio is not None and fim is not None:
        minutos = (fim - inicio).total_seconds() / 60
        if fim <= inicio:
            erros["fim_sono"] = "O fim do sono precisa ser depois do início."
        elif to_utc_ms(fim, offset_minutos) > agora_utc.timestamp() * 1000:
            erros["fim_sono"] = "O fim do sono não pode estar no futuro."
        elif minutos < DURACAO_MINIMA_MINUTOS:
            erros["fim_sono"] = f"O registro precisa ter pelo menos {DURACAO_MINIMA_MINUTOS} minutos."
        elif minutos > DURACAO_MAXIMA_MINUTOS:
            erros["fim_sono"] = "O registro pode ter no máximo 24 horas."
    elif fim is not None and to_utc_ms(fim, offset_minutos) > agora_utc.timestamp() * 1000:
        erros["fim_sono"] = "O fim do sono não pode estar no futuro."

    if dados.get("qualidade_sono") not in ROTULOS_QUALIDADE:
        erros["qualidade_sono"] = "Selecione a qualidade do sono."

    if len(str(dados.get("observacoes") or "").strip()) > TAMANHO_MAXIMO_OBSERVACOES:
        erros["observacoes"] = f"Use no máximo {TAMANHO_MAXIMO_OBSERVACOES} caracteres."

    return erros


def get_period_ms(registro: dict[str, Any]) -> tuple[int, int] | None:
    try:
        return int(registro["inicio_sono"]), int(registro["fim_sono"])
    except (KeyError, TypeError, ValueError):
        return None


def find_overlap(
    inicio_ms: int, fim_ms: int, registros: list[dict[str, Any]], ignorar_id: str = ""
) -> dict[str, Any] | None:
    """Primeiro registro que se sobrepõe ao período; períodos só encostados não contam."""
    for registro in registros:
        if ignorar_id and str(registro.get("id", "")) == ignorar_id:
            continue
        periodo = get_period_ms(registro)
        if periodo and periodo[0] < fim_ms and periodo[1] > inicio_ms:
            return registro
    return None


def format_conflict_message(registro: dict[str, Any], offset_minutos: int) -> str:
    inicio = from_utc_ms(registro.get("inicio_sono"), offset_minutos)
    fim = from_utc_ms(registro.get("fim_sono"), offset_minutos)
    periodo = f" ({format_period(inicio, fim)})" if inicio and fim else ""
    return f"Já existe um registro de sono nesse período{periodo}. Ajuste os horários."


def build_sono_payload(dados: dict[str, Any], offset_minutos: int) -> dict[str, Any]:
    """Só período, qualidade e observações: o dono e a duração vêm do servidor."""
    observacoes = str(dados.get("observacoes") or "").strip()
    return {
        "inicio_sono": to_utc_ms(parse_local_datetime(dados["inicio_sono"]), offset_minutos),
        "fim_sono": to_utc_ms(parse_local_datetime(dados["fim_sono"]), offset_minutos),
        "qualidade_sono": int(dados["qualidade_sono"]),
        "observacoes": observacoes or None,
    }


def sort_sono(registros: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mais recentes primeiro, pelo início do sono."""
    return sorted(registros, key=lambda registro: (get_period_ms(registro) or (0, 0))[0], reverse=True)


def get_duration_minutes(registro: dict[str, Any]) -> int | None:
    try:
        duracao = int(registro.get("duracao_minutos") or 0)
    except (TypeError, ValueError):
        duracao = 0
    if duracao > 0:
        return duracao
    periodo = get_period_ms(registro)
    return (periodo[1] - periodo[0]) // 60000 if periodo and periodo[1] > periodo[0] else None


def get_quality(registro: dict[str, Any]) -> int:
    try:
        qualidade = int(registro.get("qualidade_sono") or 0)
    except (TypeError, ValueError):
        return 0
    return qualidade if qualidade in ROTULOS_QUALIDADE else 0


def build_registro_view(registro: dict[str, Any], offset_minutos: int) -> dict[str, str]:
    """Dados prontos para exibir um item da lista (tudo texto, para o `rx.foreach`)."""
    inicio = from_utc_ms(registro.get("inicio_sono"), offset_minutos)
    fim = from_utc_ms(registro.get("fim_sono"), offset_minutos)
    qualidade = get_quality(registro)
    rotulo = ROTULOS_QUALIDADE.get(qualidade, "Sem avaliação")
    return {
        "id": str(registro.get("id", "")),
        # a noite é identificada pelo dia (Brasília) em que a pessoa acordou
        "data": f"{fim:%d/%m/%Y}" if fim else "",
        "intervalo": format_period(inicio, fim) if inicio and fim else "",
        "duracao": format_duration(get_duration_minutes(registro)),
        "qualidade": str(qualidade),
        "rotulo_qualidade": rotulo,
        "descricao_qualidade": f"Qualidade {qualidade} de 5: {rotulo}" if qualidade else rotulo,
        "observacoes": str(registro.get("observacoes") or ""),
    }


def get_form_values(registro: dict[str, Any], offset_minutos: int) -> dict[str, Any]:
    """Valores do formulário para editar um registro existente."""
    inicio = from_utc_ms(registro.get("inicio_sono"), offset_minutos)
    fim = from_utc_ms(registro.get("fim_sono"), offset_minutos)
    return {
        "inicio_sono": format_input_value(inicio) if inicio else "",
        "fim_sono": format_input_value(fim) if fim else "",
        "qualidade_sono": get_quality(registro),
        "observacoes": str(registro.get("observacoes") or ""),
    }


def summarize_recent_sleep(
    registros: list[dict[str, Any]], quantidade: int = 7, offset_minutos: int = FUSO_BRASILIA_OFFSET_MINUTOS
) -> dict[str, Any]:
    """Resumo das últimas `quantidade` noites para recomendações e Relatórios.

    Devolve `{quantidade, duracao_media_minutos, qualidade_media, noites}`; sem
    registros, quantidade 0 e médias None.
    """
    noites = []
    for registro in sort_sono(registros)[: max(quantidade, 0)]:
        fim = from_utc_ms(registro.get("fim_sono"), offset_minutos)
        noites.append({
            "data": fim.date().isoformat() if fim else "",
            "duracao_minutos": get_duration_minutes(registro) or 0,
            "qualidade": get_quality(registro) or None,
        })

    qualidades = [noite["qualidade"] for noite in noites if noite["qualidade"]]
    return {
        "quantidade": len(noites),
        "duracao_media_minutos": round(sum(n["duracao_minutos"] for n in noites) / len(noites), 1) if noites else None,
        "qualidade_media": round(sum(qualidades) / len(qualidades), 1) if qualidades else None,
        "noites": noites,
    }
