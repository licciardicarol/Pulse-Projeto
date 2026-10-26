"""Regras de negócio do peso corporal: validação, fuso, peso atual e variação.

Nada aqui estima ou inventa valores: o resumo usa só pesos registrados pelo
usuário, e a "falta para a meta" depende de um peso-alvo que ainda não existe.
"""

import re
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Any

# horário de Brasília; o Brasil não tem horário de verão desde 2019
FUSO_BRASILIA = timezone(timedelta(hours=-3), "BRT")

PESO_MINIMO = Decimal("20")
PESO_MAXIMO = Decimal("400")

# dígitos com até 2 casas decimais, separador vírgula ou ponto
FORMATO_PESO = re.compile(r"^\d{1,3}([.,]\d{1,2})?$")

SEM_VALOR = "—"


def now_brasilia() -> datetime:
    return datetime.now(FUSO_BRASILIA)


def parse_weight(texto: str) -> Decimal | None:
    """ "70,5" -> Decimal("70.5"); None se não for número com até 2 casas."""
    valor = str(texto or "").strip()
    if not FORMATO_PESO.match(valor):
        return None
    return Decimal(valor.replace(",", "."))


def parse_date(valor: str) -> date | None:
    try:
        return date.fromisoformat(str(valor).strip()[:10])
    except ValueError:
        return None


def parse_time(valor: str) -> time | None:
    try:
        return time.fromisoformat(str(valor).strip()[:5])
    except ValueError:
        return None


def combine_date_time(data: date, horario: time) -> datetime:
    """Data + horário informados, interpretados no horário de Brasília."""
    return datetime.combine(data, horario, tzinfo=FUSO_BRASILIA)


def validate_registro_peso(dados: dict[str, str], agora: datetime) -> dict[str, str]:
    """Devolve campo -> mensagem; dicionário vazio quando o registro pode ser salvo."""
    erros: dict[str, str] = {}

    texto_peso = str(dados.get("peso") or "").strip()
    peso = parse_weight(texto_peso)
    if not texto_peso:
        erros["peso"] = "Informe o seu peso."
    elif peso is None:
        erros["peso"] = "Use apenas números, com até 2 casas decimais (ex.: 70,5)."
    elif not PESO_MINIMO <= peso <= PESO_MAXIMO:
        erros["peso"] = "Informe um peso entre 20 e 400 kg."

    data = parse_date(dados.get("data", ""))
    horario = parse_time(dados.get("horario", ""))
    agora_brasilia = agora.astimezone(FUSO_BRASILIA)
    if data is None:
        erros["data"] = "Informe a data."
    elif data > agora_brasilia.date():
        erros["data"] = "A data não pode estar no futuro."
    if horario is None:
        erros["horario"] = "Informe o horário."
    elif data is not None and "data" not in erros and combine_date_time(data, horario) > agora_brasilia:
        erros["horario"] = "O horário não pode estar no futuro."

    return erros


def to_milliseconds(momento: datetime) -> int:
    return int(momento.timestamp() * 1000)


def from_milliseconds(valor: Any) -> datetime | None:
    """Timestamp do Xano (ms em UTC) -> horário de Brasília."""
    try:
        return datetime.fromtimestamp(int(valor) / 1000, tz=FUSO_BRASILIA)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def build_registro_payload(dados: dict[str, str]) -> dict[str, Any]:
    """Só peso e instante da pesagem: o dono vem do token no Xano."""
    momento = combine_date_time(parse_date(dados["data"]), parse_time(dados["horario"]))
    return {
        "peso": float(parse_weight(dados["peso"])),
        "data_horario": to_milliseconds(momento),
    }


def get_timestamp(registro: dict[str, Any]) -> int:
    try:
        return int(registro.get("data_horario") or 0)
    except (TypeError, ValueError):
        return 0


def get_created_at(registro: dict[str, Any]) -> int:
    try:
        return int(registro.get("created_at") or 0)
    except (TypeError, ValueError):
        return 0


def sort_registros(registros: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mais recentes primeiro pela data da pesagem (empate: o registrado por último)."""
    return sorted(registros, key=lambda registro: (get_timestamp(registro), get_created_at(registro)), reverse=True)


def get_weight(registro: dict[str, Any]) -> float | None:
    try:
        return float(registro["peso"])
    except (KeyError, TypeError, ValueError):
        return None


def get_current_weight(registros: list[dict[str, Any]]) -> float | None:
    """Peso do registro com a pesagem mais recente, não o último criado."""
    if not registros:
        return None
    return get_weight(sort_registros(registros)[0])


def calculate_change_since_first(registros: list[dict[str, Any]]) -> float | None:
    """Peso atual menos o da primeira pesagem; None com menos de 2 registros."""
    if len(registros) < 2:
        return None
    ordenados = sort_registros(registros)
    atual, primeiro = get_weight(ordenados[0]), get_weight(ordenados[-1])
    if atual is None or primeiro is None:
        return None
    return round(atual - primeiro, 2)


def format_decimal_br(valor: float) -> str:
    """70 -> "70,0"; 70.25 -> "70,25" (1 casa, ou 2 quando há centésimos)."""
    arredondado = round(abs(valor), 2)
    casas = 2 if round(arredondado * 100) % 10 else 1
    return f"{arredondado:.{casas}f}".replace(".", ",")


def format_weight(valor: float | None) -> str:
    return SEM_VALOR if valor is None else f"{format_decimal_br(valor)} kg"


def format_change(valor: float | None) -> str:
    """Diferença com sinal ("-1,2 kg", "+0,8 kg", "0,0 kg"); "—" sem base de comparação."""
    if valor is None:
        return SEM_VALOR
    sinal = "+" if valor > 0 else "-" if valor < 0 else ""
    return f"{sinal}{format_decimal_br(valor)} kg"


def format_date_time_br(momento: datetime | None) -> str:
    return momento.strftime("%d/%m/%Y · %H:%M") if momento else SEM_VALOR


def build_weight_view(registro: dict[str, Any]) -> dict[str, str]:
    """Dados prontos para exibir um item da lista (tudo texto, para o `rx.foreach`)."""
    return {
        "id": str(registro.get("id", "")),
        "peso": format_weight(get_weight(registro)),
        "data_hora": format_date_time_br(from_milliseconds(registro.get("data_horario"))),
    }
