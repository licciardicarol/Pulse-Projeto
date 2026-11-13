"""Cliente HTTP do Google Gemini: geração de JSON estruturado para o backend do Pulse.

Usado só pelo backend do Reflex: a chave fica no ambiente do servidor e nunca vai
para o navegador. `generate_json` é o ponto único de chamada; `analyze_meal` (análise
nutricional) e a recomendação do dia montam só a instrução, o prompt e o esquema.
Erros viram `GeminiError` com tipo fechado ("nao_configurado", "limite_requisicoes",
"sobrecarregado" ou "falha"), e os logs registram só a finalidade, o tipo e o status
HTTP, nunca o pedido nem a resposta.
"""

import json
import logging
import os
from typing import Any

import httpx

from projetofacul.logic.analise_refeicao import ESQUEMA_RESPOSTA, INSTRUCAO_SISTEMA, build_analysis_prompt

URL_BASE_GEMINI = "https://generativelanguage.googleapis.com/v1beta"
# estável e mais barato da linha Flash na documentação do Google (2026-11-10); trocável pelo .env
MODELO_PADRAO = "gemini-3.5-flash-lite"
TEMPO_LIMITE_SEGUNDOS = 20.0
MAXIMO_TOKENS_RESPOSTA = 1024
TEMPERATURA = 0.2
# servidor do Google sobrecarregado ou fora do ar: costuma passar em instantes
STATUS_SOBRECARREGADO = (500, 502, 503, 504)

logger = logging.getLogger(__name__)


class GeminiError(Exception):
    """Falha da IA identificada apenas pelo tipo."""

    def __init__(self, tipo: str):
        super().__init__(tipo)
        self.tipo = tipo


def get_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()


def is_configured() -> bool:
    return bool(get_api_key())


def get_model() -> str:
    return os.getenv("GEMINI_MODEL", "").strip() or MODELO_PADRAO


def create_http_client() -> httpx.AsyncClient:
    # ponto único de criação, substituído nos testes por um transporte simulado
    return httpx.AsyncClient(timeout=TEMPO_LIMITE_SEGUNDOS)


def build_request_body(
    instrucao: str, prompt: str, esquema: dict[str, Any], max_tokens: int = MAXIMO_TOKENS_RESPOSTA
) -> dict[str, Any]:
    return {
        "systemInstruction": {"parts": [{"text": instrucao}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseJsonSchema": esquema,
            "temperature": TEMPERATURA,
            "maxOutputTokens": max_tokens,
        },
    }


def extract_json(resposta: Any, finalidade: str = "pedido") -> Any:
    """Tira o JSON do texto da resposta; pedido bloqueado, corte ou texto inválido viram falha."""
    if not isinstance(resposta, dict):
        raise GeminiError("falha")

    feedback = resposta.get("promptFeedback")
    if isinstance(feedback, dict) and feedback.get("blockReason"):
        logger.warning("Gemini bloqueou o pedido (%s)", finalidade)
        raise GeminiError("falha")

    candidatos = resposta.get("candidates")
    if not isinstance(candidatos, list) or not candidatos or not isinstance(candidatos[0], dict):
        raise GeminiError("falha")

    candidato = candidatos[0]
    if candidato.get("finishReason") != "STOP":
        logger.warning(
            "Gemini terminou sem concluir (%s, finishReason=%s)", finalidade, candidato.get("finishReason")
        )
        raise GeminiError("falha")

    conteudo = candidato.get("content")
    partes = conteudo.get("parts") if isinstance(conteudo, dict) else None
    if not isinstance(partes, list):
        raise GeminiError("falha")
    # partes de raciocínio ("thought") não fazem parte da resposta
    texto = "".join(
        parte["text"]
        for parte in partes
        if isinstance(parte, dict) and isinstance(parte.get("text"), str) and not parte.get("thought")
    )

    try:
        return json.loads(texto)
    except ValueError:
        raise GeminiError("falha") from None


async def generate_json(
    instrucao: str,
    prompt: str,
    esquema: dict[str, Any],
    finalidade: str,
    max_tokens: int = MAXIMO_TOKENS_RESPOSTA,
) -> Any:
    """Pede uma resposta em JSON no formato de `esquema` e devolve o JSON decodificado (ainda não validado)."""
    chave = get_api_key()
    if not chave:
        raise GeminiError("nao_configurado")

    url = f"{URL_BASE_GEMINI}/models/{get_model()}:generateContent"
    try:
        async with create_http_client() as cliente:
            resposta = await cliente.post(
                url,
                json=build_request_body(instrucao, prompt, esquema, max_tokens),
                headers={"x-goog-api-key": chave},
            )
    except httpx.HTTPError as erro:
        logger.warning("Gemini indisponível (%s, %s)", finalidade, type(erro).__name__)
        raise GeminiError("falha") from None

    if resposta.status_code == 429:
        logger.warning("Gemini recusou o pedido (%s): limite de requisições (HTTP 429)", finalidade)
        raise GeminiError("limite_requisicoes")
    if resposta.status_code in STATUS_SOBRECARREGADO:
        logger.warning("Gemini sobrecarregado (%s, HTTP %s)", finalidade, resposta.status_code)
        raise GeminiError("sobrecarregado")
    if resposta.status_code >= 400:
        logger.warning("Gemini recusou o pedido (%s, HTTP %s)", finalidade, resposta.status_code)
        raise GeminiError("falha")

    try:
        dados = resposta.json()
    except ValueError:
        raise GeminiError("falha") from None
    return extract_json(dados, finalidade)


async def analyze_meal(tipo: str, descricao: str) -> Any:
    """Pede a estimativa nutricional da refeição e devolve o JSON decodificado (ainda não validado)."""
    return await generate_json(
        INSTRUCAO_SISTEMA, build_analysis_prompt(tipo, descricao), ESQUEMA_RESPOSTA, "análise de refeição"
    )
