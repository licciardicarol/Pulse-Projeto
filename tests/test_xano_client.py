import asyncio
import json

import httpx
import pytest

from projetofacul.auth_page import get_auth_error_message
from projetofacul.services import xano_client
from projetofacul.services.xano_client import XanoError

URL_BASE = "https://xano.teste/api:abc"


@pytest.fixture
def requisicoes(monkeypatch):
    """Substitui o HTTP real por um transporte simulado e registra as chamadas."""
    registradas: list[httpx.Request] = []
    respostas: dict[str, httpx.Response] = {}

    def responder(requisicao: httpx.Request) -> httpx.Response:
        registradas.append(requisicao)
        return respostas[requisicao.url.path.split("api:abc/")[1]]

    monkeypatch.setenv("XANO_API_URL", URL_BASE + "/")
    monkeypatch.setattr(
        xano_client,
        "create_http_client",
        lambda: httpx.AsyncClient(transport=httpx.MockTransport(responder)),
    )
    return registradas, respostas


def test_signup_envia_dados_e_retorna_token(requisicoes):
    registradas, respostas = requisicoes
    respostas["auth/signup"] = httpx.Response(200, json={"authToken": "tok-123"})

    token = asyncio.run(xano_client.signup("Ana", "ana@exemplo.com", "12345678"))

    assert token == "tok-123"
    assert registradas[0].method == "POST"
    assert str(registradas[0].url) == f"{URL_BASE}/auth/signup"
    assert json.loads(registradas[0].content) == {
        "nome": "Ana",
        "email": "ana@exemplo.com",
        "senha": "12345678",
    }


def test_rotas_autenticadas_enviam_bearer(requisicoes):
    registradas, respostas = requisicoes
    respostas["perfil/me"] = httpx.Response(200, json={"id": 1, "onboarding_concluido": False})

    perfil = asyncio.run(xano_client.get_perfil("tok-123"))

    assert perfil["onboarding_concluido"] is False
    assert registradas[0].headers["Authorization"] == "Bearer tok-123"


@pytest.mark.parametrize(
    ("status", "tipo"),
    [(400, "invalido"), (401, "nao_autorizado"), (403, "acesso_negado"), (404, "nao_encontrado"), (500, "indisponivel")],
)
def test_status_http_vira_tipo_fechado_sem_texto_do_servidor(requisicoes, status, tipo):
    _, respostas = requisicoes
    respostas["auth/login"] = httpx.Response(status, json={"message": "Invalid Credentials. stack trace"})

    with pytest.raises(XanoError) as erro:
        asyncio.run(xano_client.login("ana@exemplo.com", "senha-secreta"))

    assert erro.value.tipo == tipo
    assert "Invalid" not in str(erro.value)
    assert "senha-secreta" not in str(erro.value)


def test_falha_de_rede_vira_indisponivel(monkeypatch):
    def falhar(requisicao):
        raise httpx.ConnectTimeout("timeout", request=requisicao)

    monkeypatch.setenv("XANO_API_URL", URL_BASE)
    monkeypatch.setattr(
        xano_client,
        "create_http_client",
        lambda: httpx.AsyncClient(transport=httpx.MockTransport(falhar)),
    )

    with pytest.raises(XanoError) as erro:
        asyncio.run(xano_client.login("ana@exemplo.com", "12345678"))

    assert erro.value.tipo == "indisponivel"


def test_resposta_sem_token_e_tratada_como_falha(requisicoes):
    _, respostas = requisicoes
    respostas["auth/login"] = httpx.Response(200, json={})

    with pytest.raises(XanoError) as erro:
        asyncio.run(xano_client.login("ana@exemplo.com", "12345678"))

    assert erro.value.tipo == "indisponivel"


def test_url_ausente_nao_faz_chamada(monkeypatch):
    monkeypatch.delenv("XANO_API_URL", raising=False)

    with pytest.raises(XanoError) as erro:
        asyncio.run(xano_client.login("ana@exemplo.com", "12345678"))

    assert erro.value.tipo == "nao_configurado"


def test_mensagens_de_autenticacao_sao_genericas():
    assert get_auth_error_message("login", "acesso_negado") == "E-mail ou senha incorretos."
    assert get_auth_error_message("login", "nao_autorizado") == "E-mail ou senha incorretos."
    assert "Entrar" in get_auth_error_message("cadastro", "acesso_negado")
    assert get_auth_error_message("cadastro", "nao_configurado") == "O acesso está temporariamente indisponível."
    for modo in ("login", "cadastro"):
        mensagem = get_auth_error_message(modo, "indisponivel")
        assert "Tente novamente" in mensagem
