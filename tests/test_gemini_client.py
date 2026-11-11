import asyncio
import json
import logging

import httpx
import pytest

from projetofacul.logic.analise_refeicao import ESQUEMA_RESPOSTA, INSTRUCAO_SISTEMA
from projetofacul.services import gemini_client
from projetofacul.services.gemini_client import GeminiError

CHAVE = "chave-gemini-de-teste"
DESCRICAO = "2 ovos mexidos e 1 pão francês"
ANALISE = {
    "reconhecido": True,
    "resumo": "2 ovos mexidos (~180 kcal), 1 pão francês (~135 kcal)",
    "calorias": 315,
    "proteinas": 17,
    "carboidratos": 29,
    "gorduras": 14,
}


def resposta_gemini(texto: str, finish: str = "STOP", **extra) -> dict:
    return {
        "candidates": [{"content": {"role": "model", "parts": [{"text": texto}]}, "finishReason": finish}],
        **extra,
    }


@pytest.fixture
def gemini(monkeypatch):
    """Troca o HTTP real por um transporte simulado; `respostas[0]` responde a próxima chamada."""
    registradas: list[httpx.Request] = []
    respostas: list = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        registradas.append(requisicao)
        resposta = respostas.pop(0)
        if isinstance(resposta, Exception):
            raise resposta
        return resposta

    monkeypatch.setenv("GEMINI_API_KEY", CHAVE)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setattr(
        gemini_client,
        "create_http_client",
        lambda: httpx.AsyncClient(transport=httpx.MockTransport(responder)),
    )
    return registradas, respostas


def analisar():
    return asyncio.run(gemini_client.analyze_meal("Café da manhã", DESCRICAO))


def test_pede_json_estruturado_ao_modelo_padrao_com_a_chave_no_cabecalho(gemini):
    registradas, respostas = gemini
    respostas.append(httpx.Response(200, json=resposta_gemini(json.dumps(ANALISE))))

    assert analisar() == ANALISE

    requisicao = registradas[0]
    assert requisicao.method == "POST"
    assert str(requisicao.url) == (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"
    )
    assert requisicao.headers["x-goog-api-key"] == CHAVE
    # a chave nunca vai na URL
    assert CHAVE not in str(requisicao.url)

    corpo = json.loads(requisicao.content)
    assert corpo["systemInstruction"]["parts"][0]["text"] == INSTRUCAO_SISTEMA
    assert corpo["generationConfig"]["responseMimeType"] == "application/json"
    assert corpo["generationConfig"]["responseJsonSchema"] == ESQUEMA_RESPOSTA
    texto_usuario = corpo["contents"][0]["parts"][0]["text"]
    assert "Café da manhã" in texto_usuario and DESCRICAO in texto_usuario


def test_modelo_configuravel_pelo_ambiente(gemini, monkeypatch):
    registradas, respostas = gemini
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.6-flash")
    respostas.append(httpx.Response(200, json=resposta_gemini(json.dumps(ANALISE))))

    analisar()

    assert "/models/gemini-3.6-flash:generateContent" in str(registradas[0].url)


def test_sem_chave_nao_faz_requisicao(gemini, monkeypatch):
    registradas, _ = gemini
    monkeypatch.setenv("GEMINI_API_KEY", "  ")

    with pytest.raises(GeminiError) as erro:
        analisar()

    assert erro.value.tipo == "nao_configurado"
    assert registradas == []
    assert gemini_client.is_configured() is False


def test_limite_de_requisicoes(gemini):
    _, respostas = gemini
    respostas.append(httpx.Response(429, json={"error": {"status": "RESOURCE_EXHAUSTED"}}))

    with pytest.raises(GeminiError) as erro:
        analisar()

    assert erro.value.tipo == "limite_requisicoes"


@pytest.mark.parametrize(
    "resposta",
    [
        httpx.ReadTimeout("demorou"),
        httpx.ConnectError("sem rede"),
        httpx.Response(500, json={"error": {}}),
        httpx.Response(403, json={"error": {"status": "PERMISSION_DENIED"}}),
        httpx.Response(200, text="isto não é json"),
        httpx.Response(200, json={"promptFeedback": {"blockReason": "SAFETY"}}),
        httpx.Response(200, json=resposta_gemini(json.dumps(ANALISE), finish="MAX_TOKENS")),
        httpx.Response(200, json=resposta_gemini(json.dumps(ANALISE), finish="SAFETY")),
        httpx.Response(200, json=resposta_gemini("Claro! Aqui está: {calorias: 300}")),
        httpx.Response(200, json=resposta_gemini("")),
        httpx.Response(200, json={"candidates": []}),
    ],
)
def test_demais_falhas_viram_falha(gemini, resposta):
    _, respostas = gemini
    respostas.append(resposta)

    with pytest.raises(GeminiError) as erro:
        analisar()

    assert erro.value.tipo == "falha"


def test_ignora_partes_de_raciocinio(gemini):
    _, respostas = gemini
    corpo = {
        "candidates": [
            {
                "content": {"parts": [{"text": "pensando...", "thought": True}, {"text": json.dumps(ANALISE)}]},
                "finishReason": "STOP",
            }
        ]
    }
    respostas.append(httpx.Response(200, json=corpo))

    assert analisar() == ANALISE


def test_logs_nao_mostram_refeicao_nem_chave(gemini, caplog):
    _, respostas = gemini
    respostas.append(httpx.Response(500, json={"error": {"message": DESCRICAO}}))

    with caplog.at_level(logging.WARNING, logger="projetofacul.services.gemini_client"):
        with pytest.raises(GeminiError):
            analisar()

    assert "HTTP 500" in caplog.text
    assert DESCRICAO not in caplog.text
    assert CHAVE not in caplog.text
