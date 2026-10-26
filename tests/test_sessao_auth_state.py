import asyncio

import pytest
from reflex.istate.data import RouterData
from reflex.state import State

import projetofacul.projetofacul  # noqa: F401  registra as páginas e os States
from projetofacul.auth_page import AuthState
from projetofacul.services import xano_client
from projetofacul.services.xano_client import MENSAGEM_LIMITE_REQUISICOES, XanoError
from projetofacul.states.sessao_state import VALIDADE_CONFIRMACAO_SEGUNDOS, SessaoState

USUARIO = {"id": 7, "nome": "Ana Souza", "email": "ana@exemplo.com"}


def get_substate(raiz: State, classe):
    return raiz.get_substate(classe.get_full_name().split(".")[1:])


def set_route(raiz: State, rota: str):
    raiz.router = RouterData.from_router_data({"pathname": rota, "asPath": rota, "query": {}, "headers": {}})


@pytest.fixture
def raiz():
    return State(_reflex_internal_init=True)


@pytest.fixture
def xano(monkeypatch):
    """Xano simulado: cada chave guarda um resultado (dict/str) ou um XanoError."""
    respostas = {
        "get_me": dict(USUARIO),
        "get_perfil": {"id": 3, "user_id": 7, "onboarding_concluido": False},
        "signup": "tok-novo",
        "login": "tok-login",
    }
    chamadas: list[tuple] = []

    def simular(nome):
        async def chamada(*args):
            chamadas.append((nome, args))
            resultado = respostas[nome]
            if isinstance(resultado, Exception):
                raise resultado
            return resultado

        return chamada

    for nome in respostas:
        monkeypatch.setattr(xano_client, nome, simular(nome))
    return respostas, chamadas


def run_events(geradora) -> list:
    async def coletar():
        retorno = geradora
        if hasattr(retorno, "__aiter__"):
            return [evento async for evento in retorno if evento is not None]
        resultado = await retorno
        return [resultado] if resultado is not None else []

    return asyncio.run(coletar())


def get_redirects(eventos: list) -> list[str]:
    destinos = []
    for evento in eventos:
        for nome, valor in getattr(evento, "args", ()):
            if nome._js_expr == "path":
                destinos.append(valor._var_value)
    return destinos


# --- SessaoState ---------------------------------------------------------------


def test_sem_token_rota_privada_vai_para_login(raiz, xano):
    _, chamadas = xano
    sessao = get_substate(raiz, SessaoState)
    set_route(raiz, "/perfil")

    eventos = run_events(SessaoState.ensure_session.fn(sessao))

    assert get_redirects(eventos) == ["/login"]
    assert sessao.sessao_verificada is False
    assert chamadas == []


def test_token_invalido_descarta_sessao_e_vai_para_login(raiz, xano):
    respostas, _ = xano
    respostas["get_me"] = XanoError("nao_autorizado")
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-expirado"
    set_route(raiz, "/inicio")

    eventos = run_events(SessaoState.ensure_session.fn(sessao))

    assert get_redirects(eventos) == ["/login"]
    assert sessao.token == ""


def test_onboarding_pendente_forca_perfil(raiz, xano):
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    set_route(raiz, "/treinos")

    eventos = run_events(SessaoState.ensure_session.fn(sessao))

    assert get_redirects(eventos) == ["/perfil"]
    assert sessao.sessao_verificada is False


def test_sessao_valida_libera_pagina_e_carrega_usuario(raiz, xano):
    respostas, _ = xano
    respostas["get_perfil"]["onboarding_concluido"] = True
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    set_route(raiz, "/treinos")

    eventos = run_events(SessaoState.ensure_session.fn(sessao))

    assert get_redirects(eventos) == []
    assert sessao.sessao_verificada is True
    assert sessao.usuario_nome == "Ana Souza"
    assert sessao.usuario_email == "ana@exemplo.com"


def test_xano_indisponivel_mostra_erro_sem_derrubar_sessao(raiz, xano):
    respostas, _ = xano
    respostas["get_me"] = XanoError("indisponivel")
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    set_route(raiz, "/perfil")

    eventos = run_events(SessaoState.ensure_session.fn(sessao))

    assert get_redirects(eventos) == []
    assert sessao.token == "tok-123"
    assert sessao.sessao_verificada is False
    assert "Tente novamente" in sessao.erro_sessao


def confirm_session(raiz: State, rota: str = "/treinos") -> SessaoState:
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    set_route(raiz, rota)
    run_events(SessaoState.ensure_session.fn(sessao))
    return sessao


def count_calls(chamadas: list, nome: str) -> int:
    return sum(1 for chamada in chamadas if chamada[0] == nome)


def test_confirmacao_recente_e_reaproveitada_entre_paginas(raiz, xano):
    respostas, chamadas = xano
    respostas["get_perfil"]["onboarding_concluido"] = True
    sessao = confirm_session(raiz)

    for rota in ("/refeicoes", "/sono", "/peso", "/perfil"):
        set_route(raiz, rota)
        eventos = run_events(SessaoState.ensure_session.fn(sessao))
        assert get_redirects(eventos) == []
        assert sessao.sessao_verificada is True

    assert count_calls(chamadas, "get_me") == 1
    assert count_calls(chamadas, "get_perfil") == 1


def test_confirmacao_expirada_consulta_o_xano_de_novo(raiz, xano):
    respostas, chamadas = xano
    respostas["get_perfil"]["onboarding_concluido"] = True
    sessao = confirm_session(raiz)
    sessao._verificada_em -= VALIDADE_CONFIRMACAO_SEGUNDOS + 1

    run_events(SessaoState.ensure_session.fn(sessao))

    assert count_calls(chamadas, "get_me") == 2


def test_token_diferente_nao_usa_confirmacao_anterior(raiz, xano):
    respostas, chamadas = xano
    respostas["get_perfil"]["onboarding_concluido"] = True
    sessao = confirm_session(raiz)
    sessao.token = "tok-outro"

    run_events(SessaoState.ensure_session.fn(sessao))

    assert count_calls(chamadas, "get_me") == 2


def test_sair_descarta_confirmacao(raiz, xano):
    respostas, chamadas = xano
    respostas["get_perfil"]["onboarding_concluido"] = True
    sessao = confirm_session(raiz)

    SessaoState.logout.fn(sessao)
    confirm_session(raiz)

    assert count_calls(chamadas, "get_me") == 2


def test_limite_do_xano_mostra_mensagem_e_mantem_token(raiz, xano):
    respostas, _ = xano
    respostas["get_me"] = XanoError("limite_requisicoes")
    sessao = confirm_session(raiz, "/refeicoes")

    assert sessao.erro_sessao == MENSAGEM_LIMITE_REQUISICOES
    assert sessao.token == "tok-123"
    assert sessao.sessao_verificada is False


def test_tentar_novamente_recarrega_a_pagina(raiz):
    sessao = get_substate(raiz, SessaoState)
    sessao.erro_sessao = MENSAGEM_LIMITE_REQUISICOES

    evento = SessaoState.retry_session.fn(sessao)

    assert "window.location.reload()" in str(evento)
    assert sessao.erro_sessao == ""


def test_logado_em_login_vai_para_o_app(raiz, xano):
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    set_route(raiz, "/login")

    eventos = run_events(SessaoState.redirect_if_authenticated.fn(sessao))

    assert get_redirects(eventos) == ["/perfil"]


def test_sair_limpa_tudo_e_vai_para_home(raiz):
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    sessao.usuario_nome = "Ana"
    sessao.sessao_verificada = True
    sessao._perfil = {"id": 3}

    evento = SessaoState.logout.fn(sessao)

    assert get_redirects([evento]) == ["/"]
    assert sessao.token == ""
    assert sessao.usuario_nome == ""
    assert sessao.sessao_verificada is False
    assert sessao._perfil == {}


# --- AuthState -----------------------------------------------------------------


def submit(raiz: State, modo: str, **campos) -> list:
    auth = get_substate(raiz, AuthState)
    auth.modo = modo
    dados = {"nome": "", "email": "", "senha": "", "confirmar_senha": "", **campos}
    return run_events(AuthState.enviar.fn(auth, dados))


def test_cadastro_valido_cria_sessao_e_vai_para_perfil(raiz, xano):
    _, chamadas = xano

    eventos = submit(
        raiz, "cadastro", nome=" Ana ", email=" ANA@Exemplo.com ", senha="12345678", confirmar_senha="12345678"
    )

    assert ("signup", ("Ana", "ana@exemplo.com", "12345678")) in chamadas
    assert get_substate(raiz, SessaoState).token == "tok-novo"
    assert get_redirects(eventos) == ["/perfil"]
    auth = get_substate(raiz, AuthState)
    assert auth.senha == "" and auth.confirmar_senha == ""
    assert auth.enviando is False


def test_login_com_onboarding_concluido_vai_para_inicio(raiz, xano):
    respostas, _ = xano
    respostas["get_perfil"]["onboarding_concluido"] = True

    eventos = submit(raiz, "login", email="ana@exemplo.com", senha="12345678")

    assert get_redirects(eventos) == ["/inicio"]


def test_credenciais_invalidas_nao_criam_sessao(raiz, xano):
    respostas, _ = xano
    respostas["login"] = XanoError("acesso_negado")

    eventos = submit(raiz, "login", email="ana@exemplo.com", senha="senhaErrada")

    auth = get_substate(raiz, AuthState)
    assert get_redirects(eventos) == []
    assert get_substate(raiz, SessaoState).token == ""
    assert auth.erro_geral == "E-mail ou senha incorretos."
    assert "senhaErrada" not in auth.erro_geral
    assert auth.enviando is False


def test_xano_indisponivel_nao_cria_sessao(raiz, xano):
    respostas, _ = xano
    respostas["signup"] = XanoError("indisponivel")

    eventos = submit(raiz, "cadastro", nome="Ana", email="ana@exemplo.com", senha="12345678", confirmar_senha="12345678")

    assert get_redirects(eventos) == []
    assert get_substate(raiz, SessaoState).token == ""
    assert "Tente novamente" in get_substate(raiz, AuthState).erro_geral


def test_validacao_local_bloqueia_envio(raiz, xano):
    _, chamadas = xano

    submit(raiz, "cadastro", nome="", email="invalido", senha="123", confirmar_senha="456")

    auth = get_substate(raiz, AuthState)
    assert chamadas == []
    assert auth.erro_nome and auth.erro_email and auth.erro_senha and auth.erro_confirmacao


def test_envio_em_andamento_ignora_segundo_envio(raiz, xano):
    _, chamadas = xano
    get_substate(raiz, AuthState).enviando = True

    submit(raiz, "login", email="ana@exemplo.com", senha="12345678")

    assert chamadas == []
