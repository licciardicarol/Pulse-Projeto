import pytest

from projetofacul.logic.navegacao import ROTAS_PRIVADAS, resolve_redirect


@pytest.mark.parametrize("rota", ROTAS_PRIVADAS)
def test_rota_privada_sem_sessao_vai_para_login(rota):
    assert resolve_redirect(False, False, rota) == "/login"
    assert resolve_redirect(False, True, rota) == "/login"


@pytest.mark.parametrize("rota", [r for r in ROTAS_PRIVADAS if r != "/perfil"])
def test_onboarding_pendente_forca_perfil(rota):
    assert resolve_redirect(True, False, rota) == "/perfil"


def test_onboarding_pendente_permite_perfil():
    assert resolve_redirect(True, False, "/perfil") is None


@pytest.mark.parametrize("rota", ROTAS_PRIVADAS)
def test_onboarding_concluido_libera_rotas_privadas(rota):
    assert resolve_redirect(True, True, rota) is None


@pytest.mark.parametrize("rota", ["/login", "/cadastro"])
def test_usuario_logado_nao_fica_nas_telas_de_acesso(rota):
    assert resolve_redirect(True, False, rota) == "/perfil"
    assert resolve_redirect(True, True, rota) == "/inicio"
    assert resolve_redirect(False, False, rota) is None


def test_rotas_publicas_nunca_redirecionam():
    assert resolve_redirect(False, False, "/") is None
    assert resolve_redirect(True, True, "/") is None


def test_rota_normalizada():
    assert resolve_redirect(False, False, "/perfil/") == "/login"
    assert resolve_redirect(True, False, "/Treinos") == "/perfil"
