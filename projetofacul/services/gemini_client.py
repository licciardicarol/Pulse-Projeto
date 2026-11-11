"""Cliente HTTP do Google Gemini para a análise nutricional das refeições.

Usado só pelo backend do Reflex: a chave fica no ambiente do servidor e nunca vai
para o navegador. A IA recebe apenas o tipo e a descrição da refeição. Erros viram
`GeminiError` com tipo fechado ("nao_configurado", "limite_requisicoes" ou "falha"),
e os logs registram só o tipo e o status HTTP, nunca a refeição nem a resposta.
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


def build_request_body(tipo: str, descricao: str) -> dict[str, Any]:
    return {
        "systemInstruction": {"parts": [{"text": INSTRUCAO_SISTEMA}]},
        "contents": [{"role": "user", "parts": [{"text": build_analysis_prompt(tipo, descricao)}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseJsonSchema": ESQUEMA_RESPOSTA,
            "temperature": TEMPERATURA,
            "maxOutputTokens": MAXIMO_TOKENS_RESPOSTA,
        },
    }


def extract_json(resposta: Any) -> Any:
    """Tira o JSON do texto da resposta; pedido bloqueado, corte ou texto inválido viram falha."""
    if not isinstance(resposta, dict):
        raise GeminiError("falha")

    feedback = resposta.get("promptFeedback")
    if isinstance(feedback, dict) and feedback.get("blockReason"):
        logger.warning("Gemini bloqueou o pedido da análise de refeição")
        raise GeminiError("falha")

    candidatos = resposta.get("candidates")
    if not isinstance(candidatos, list) or not candidatos or not isinstance(candidatos[0], dict):
        raise GeminiError("falha")

    candidato = candidatos[0]
    if candidato.get("finishReason") != "STOP":
        logger.warning("Gemini terminou a análise sem concluir (finishReason=%s)", candidato.get("finishReason"))
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


async def analyze_meal(tipo: str, descricao: str) -> Any:
    """Pede a estimativa nutricional da refeição e devolve o JSON decodificado (ainda não validado)."""
    chave = get_api_key()
    if not chave:
        raise GeminiError("nao_configurado")

    url = f"{URL_BASE_GEMINI}/models/{get_model()}:generateContent"
    try:
        async with create_http_client() as cliente:
            resposta = await cliente.post(
                url,
                json=build_request_body(tipo, descricao),
                headers={"x-goog-api-key": chave},
            )
    except httpx.HTTPError as erro:
        logger.warning("Gemini indisponível na análise de refeição (%s)", type(erro).__name__)
        raise GeminiError("falha") from None

    if resposta.status_code == 429:
        logger.warning("Gemini recusou a análise de refeição: limite de requisições (HTTP 429)")
        raise GeminiError("limite_requisicoes")
    if resposta.status_code >= 400:
        logger.warning("Gemini recusou a análise de refeição (HTTP %s)", resposta.status_code)
        raise GeminiError("falha")

    try:
        dados = resposta.json()
    except ValueError:
        raise GeminiError("falha") from None
    return extract_json(dados)
