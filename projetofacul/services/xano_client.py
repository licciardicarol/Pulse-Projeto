"""Cliente HTTP do Xano.

Usado só pelo backend do Reflex: o token e as senhas nunca saem do servidor
para outro destino além do Xano. Erros viram `XanoError` com um tipo fechado,
sem carregar textos do servidor, para a UI nunca exibir detalhes técnicos.
"""

import os
from typing import Any

import httpx

TEMPO_LIMITE_SEGUNDOS = 15.0

TIPOS_POR_STATUS = {
    400: "invalido",
    401: "nao_autorizado",
    403: "acesso_negado",
    404: "nao_encontrado",
    409: "conflito",
    422: "invalido",
    # plano gratuito do Xano: 10 requisições a cada 20 segundos
    429: "limite_requisicoes",
}

MENSAGEM_LIMITE_REQUISICOES = "Muitas ações em pouco tempo. Aguarde alguns segundos e tente novamente."


class XanoError(Exception):
    """Falha de integração identificada apenas pelo tipo."""

    def __init__(self, tipo: str):
        super().__init__(tipo)
        self.tipo = tipo


def get_base_url() -> str:
    url_base = os.getenv("XANO_API_URL", "").strip().rstrip("/")
    if not url_base:
        raise XanoError("nao_configurado")
    return url_base


def create_http_client() -> httpx.AsyncClient:
    # ponto único de criação, substituído nos testes por um transporte simulado
    return httpx.AsyncClient(timeout=TEMPO_LIMITE_SEGUNDOS)


async def send_request(
    metodo: str,
    caminho: str,
    token: str = "",
    corpo: dict[str, Any] | None = None,
) -> Any:
    url = f"{get_base_url()}/{caminho.lstrip('/')}"
    cabecalhos = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        async with create_http_client() as cliente:
            resposta = await cliente.request(metodo, url, json=corpo, headers=cabecalhos)
    except httpx.HTTPError:
        raise XanoError("indisponivel") from None

    if resposta.status_code >= 400:
        raise XanoError(TIPOS_POR_STATUS.get(resposta.status_code, "indisponivel"))

    try:
        return resposta.json()
    except ValueError:
        raise XanoError("indisponivel") from None


def get_token(resposta: Any) -> str:
    token = resposta.get("authToken") if isinstance(resposta, dict) else None
    if not isinstance(token, str) or not token:
        raise XanoError("indisponivel")
    return token


async def signup(nome: str, email: str, senha: str) -> str:
    resposta = await send_request(
        "POST", "auth/signup", corpo={"nome": nome, "email": email, "senha": senha}
    )
    return get_token(resposta)


async def login(email: str, senha: str) -> str:
    resposta = await send_request("POST", "auth/login", corpo={"email": email, "senha": senha})
    return get_token(resposta)


async def get_me(token: str) -> dict[str, Any]:
    return await send_request("GET", "auth/me", token=token)


async def get_perfil(token: str) -> dict[str, Any]:
    return await send_request("GET", "perfil/me", token=token)


async def update_perfil(token: str, dados: dict[str, Any]) -> dict[str, Any]:
    return await send_request("PATCH", "perfil/me", token=token, corpo=dados)


async def change_email(token: str, email: str, senha_atual: str) -> dict[str, Any]:
    return await send_request(
        "PATCH", "auth/me/email", token=token, corpo={"email": email, "senha_atual": senha_atual}
    )


async def change_password(token: str, senha_atual: str, nova_senha: str) -> dict[str, Any]:
    return await send_request(
        "PATCH",
        "auth/me/password",
        token=token,
        corpo={"senha_atual": senha_atual, "nova_senha": nova_senha},
    )


async def list_refeicoes(token: str) -> list[dict[str, Any]]:
    resposta = await send_request("GET", "refeicoes/me", token=token)
    return resposta if isinstance(resposta, list) else []


async def create_refeicao(token: str, data_refeicao: str, tipo: str, descricao: str) -> dict[str, Any]:
    # só estes três campos: o dono vem do token e os valores nutricionais, da IA (futura)
    return await send_request(
        "POST",
        "refeicoes/me",
        token=token,
        corpo={"data_refeicao": data_refeicao, "tipo": tipo, "descricao": descricao},
    )


async def delete_refeicao(token: str, refeicao_id: int) -> dict[str, Any]:
    return await send_request("DELETE", f"refeicoes/me/{int(refeicao_id)}", token=token)


async def list_sono(token: str) -> list[dict[str, Any]]:
    """Registros de sono do usuário; também é a fonte do resumo para recomendações e Relatórios."""
    resposta = await send_request("GET", "sono/me", token=token)
    return resposta if isinstance(resposta, list) else []


def build_sono_body(inicio_sono: int, fim_sono: int, qualidade_sono: int, observacoes: str | None) -> dict[str, Any]:
    # o dono vem do token e a duração é calculada pelo servidor
    return {
        "inicio_sono": int(inicio_sono),
        "fim_sono": int(fim_sono),
        "qualidade_sono": int(qualidade_sono),
        "observacoes": observacoes,
    }


async def create_sono(
    token: str, inicio_sono: int, fim_sono: int, qualidade_sono: int, observacoes: str | None
) -> dict[str, Any]:
    return await send_request(
        "POST", "sono/me", token=token, corpo=build_sono_body(inicio_sono, fim_sono, qualidade_sono, observacoes)
    )


async def update_sono(
    token: str, sono_id: int, inicio_sono: int, fim_sono: int, qualidade_sono: int, observacoes: str | None
) -> dict[str, Any]:
    return await send_request(
        "PATCH",
        f"sono/me/{int(sono_id)}",
        token=token,
        corpo=build_sono_body(inicio_sono, fim_sono, qualidade_sono, observacoes),
    )


async def delete_sono(token: str, sono_id: int) -> dict[str, Any]:
    return await send_request("DELETE", f"sono/me/{int(sono_id)}", token=token)
