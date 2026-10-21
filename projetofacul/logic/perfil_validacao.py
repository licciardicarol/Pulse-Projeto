"""Validação e conversão dos dados do Perfil, sem Reflex e sem rede.

Os valores do formulário chegam como texto (inputs HTML); o Xano recebe e
devolve tipos reais. As faixas repetem os filtros do `PATCH perfil/me`.
"""

import math
from datetime import date
from typing import Any

from projetofacul.logic.perfil_opcoes import (
    OPCOES_CONDICIONAMENTO,
    OPCOES_HORARIO,
    OPCOES_MODALIDADES,
    OPCOES_OBJETIVO,
    OPCOES_SEXO,
    VALORES_BIOTIPO,
)

TAMANHO_MAXIMO_NOME = 50
DATA_MINIMA_NASCIMENTO = date(1900, 1, 1)
ALTURA_MINIMA_CM = 100
ALTURA_MAXIMA_CM = 250
META_SEMANAL_MINIMA = 1
META_SEMANAL_MAXIMA = 14

# campo de texto do formulário -> opções aceitas (selects e biotipo)
OPCOES_POR_CAMPO = {
    "sexo": OPCOES_SEXO,
    "tipo_fisico": VALORES_BIOTIPO,
    "nivel_fisico": OPCOES_CONDICIONAMENTO,
    "horario_fav_de_treino": OPCOES_HORARIO,
    "objetivo": OPCOES_OBJETIVO,
}

MENSAGENS_SELECAO = {
    "sexo": "Selecione o sexo.",
    "tipo_fisico": "Selecione o biotipo que mais se parece com você.",
    "nivel_fisico": "Selecione seu condicionamento.",
    "horario_fav_de_treino": "Selecione o horário habitual.",
    "objetivo": "Selecione seu objetivo.",
}


def parse_date(texto: Any) -> date | None:
    try:
        return date.fromisoformat(str(texto or "").strip())
    except ValueError:
        return None


def parse_decimal(texto: Any) -> float | None:
    try:
        numero = float(str(texto or "").strip().replace(",", "."))
    except ValueError:
        return None
    return numero if math.isfinite(numero) else None


def parse_integer(texto: Any) -> int | None:
    numero = parse_decimal(texto)
    if numero is None or not numero.is_integer():
        return None
    return int(numero)


def validate_perfil(dados: dict[str, Any], hoje: date) -> dict[str, str]:
    """Retorna campo -> mensagem; vazio quando o Perfil pode ser salvo."""
    erros: dict[str, str] = {}

    nome = str(dados.get("nome") or "").strip()
    if not nome:
        erros["nome"] = "Informe seu nome completo."
    elif len(nome) > TAMANHO_MAXIMO_NOME:
        erros["nome"] = f"Use no máximo {TAMANHO_MAXIMO_NOME} caracteres."

    nascimento = parse_date(dados.get("data_de_nascimento"))
    if nascimento is None:
        erros["data_de_nascimento"] = "Informe sua data de nascimento."
    elif not DATA_MINIMA_NASCIMENTO <= nascimento < hoje:
        erros["data_de_nascimento"] = "Informe uma data de nascimento válida."

    altura_texto = str(dados.get("altura_cm") or "").strip()
    altura = parse_decimal(altura_texto)
    if not altura_texto:
        erros["altura_cm"] = "Informe sua altura em cm."
    elif altura is None or not ALTURA_MINIMA_CM <= altura <= ALTURA_MAXIMA_CM:
        erros["altura_cm"] = f"Informe uma altura entre {ALTURA_MINIMA_CM} e {ALTURA_MAXIMA_CM} cm."

    meta_texto = str(dados.get("meta_semanal") or "").strip()
    meta = parse_integer(meta_texto)
    if not meta_texto:
        erros["meta_semanal"] = "Informe quantos treinos pretende fazer na semana."
    elif meta is None or not META_SEMANAL_MINIMA <= meta <= META_SEMANAL_MAXIMA:
        erros["meta_semanal"] = (
            f"Informe um número inteiro entre {META_SEMANAL_MINIMA} e {META_SEMANAL_MAXIMA}."
        )

    # "Selecione" chega como texto vazio e cai aqui como qualquer valor fora da lista
    for campo, opcoes in OPCOES_POR_CAMPO.items():
        if dados.get(campo) not in opcoes:
            erros[campo] = MENSAGENS_SELECAO[campo]

    modalidades = dados.get("modalidade_fav1") or []
    if not modalidades or any(modalidade not in OPCOES_MODALIDADES for modalidade in modalidades):
        erros["modalidade_fav1"] = "Selecione pelo menos uma modalidade."

    return erros


def build_perfil_payload(dados: dict[str, Any], medidas: bool) -> dict[str, Any]:
    """Monta o corpo do `PATCH perfil/me`; chamar só com dados já validados."""
    modalidades = set(dados["modalidade_fav1"])
    return {
        "nome": str(dados["nome"]).strip(),
        "data_de_nascimento": parse_date(dados["data_de_nascimento"]).isoformat(),
        "sexo": dados["sexo"],
        "altura_cm": parse_decimal(dados["altura_cm"]),
        "tipo_fisico": dados["tipo_fisico"],
        "nivel_fisico": dados["nivel_fisico"],
        # ordem fixa das opções, sem repetições
        "modalidade_fav1": [opcao for opcao in OPCOES_MODALIDADES if opcao in modalidades],
        "horario_fav_de_treino": dados["horario_fav_de_treino"],
        "meta_semanal": parse_integer(dados["meta_semanal"]),
        "objetivo": dados["objetivo"],
        "medidas": medidas,
    }


def format_number(valor: Any) -> str:
    numero = parse_decimal(valor)
    if numero is None:
        return ""
    return str(int(numero)) if numero.is_integer() else str(numero)


def build_form_from_perfil(perfil: dict[str, Any]) -> dict[str, Any]:
    """Converte o Perfil do Xano nos textos do formulário.

    Valores fora das opções atuais (ex.: gravados antes da troca dos enums)
    viram vazios, para a pessoa escolher de novo em vez de salvar algo inválido.
    """
    formulario: dict[str, Any] = {
        "nome": str(perfil.get("nome") or ""),
        "data_de_nascimento": str(perfil.get("data_de_nascimento") or "")[:10],
        "altura_cm": format_number(perfil.get("altura_cm")),
        "meta_semanal": format_number(perfil.get("meta_semanal")),
        "modalidade_fav1": [
            opcao for opcao in OPCOES_MODALIDADES if opcao in (perfil.get("modalidade_fav1") or [])
        ],
    }
    for campo, opcoes in OPCOES_POR_CAMPO.items():
        valor = perfil.get(campo)
        formulario[campo] = valor if valor in opcoes else ""
    return formulario
