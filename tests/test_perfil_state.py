import asyncio

import pytest
from reflex.state import State

import projetofacul.projetofacul  # noqa: F401  registra as páginas e os States
from projetofacul.services import xano_client
from projetofacul.services.xano_client import XanoError
from projetofacul.states.perfil_state import MENSAGEM_FALHA_SALVAR, PerfilState
from projetofacul.states.sessao_state import SessaoState

PERFIL_SALVO = {
    "nome": "Ana Souza",
    "data_de_nascimento": "1995-04-20",
    "sexo": "Feminino",
    "altura_cm": 165,
    "tipo_fisico": "Mesomorfo",
    "nivel_fisico": "Intermediário",
    "horario_fav_de_treino": "Manhã",
    "meta_semanal": 4,
    "objetivo": "Ganhar massa",
    "modalidade_fav1": ["Musculação", "Yoga"],
    "medidas": True,
    "onboarding_concluido": False,
}


def get_substate(raiz: State, classe):
    return raiz.get_substate(classe.get_full_name().split(".")[1:])


@pytest.fixture
def estados():
    raiz = State(_reflex_internal_init=True)
    perfil = get_substate(raiz, PerfilState)
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    sessao.sessao_verificada = True
    sessao.onboarding_concluido = False
    sessao._perfil = dict(PERFIL_SALVO)
    return perfil, sessao


@pytest.fixture
def chamadas(monkeypatch):
    """Substitui o PATCH perfil/me; `resultado` pode ser um dict ou um XanoError."""
    registro = {"chamadas": [], "resultado": {"id": 1, "onboarding_concluido": True}}

    async def update_perfil_simulado(token, dados):
        registro["chamadas"].append((token, dados))
        if isinstance(registro["resultado"], Exception):
            raise registro["resultado"]
        return registro["resultado"]

    monkeypatch.setattr(xano_client, "update_perfil", update_perfil_simulado)
    return registro


def run_save(perfil: PerfilState) -> list:
    async def coletar():
        return [evento async for evento in PerfilState.save_profile.fn(perfil) if evento is not None]

    return asyncio.run(coletar())


def get_redirects(eventos: list) -> list[str]:
    destinos = []
    for evento in eventos:
        for nome, valor in getattr(evento, "args", ()):
            if nome._js_expr == "path":
                destinos.append(valor._var_value)
    return destinos


def has_toast(eventos: list, texto: str) -> bool:
    return any("__toast" in str(evento) and texto in str(evento) for evento in eventos)


def test_carregar_preenche_formulario_com_perfil_da_sessao(estados):
    perfil, _ = estados

    asyncio.run(PerfilState.load_profile.fn(perfil))

    assert perfil.nome == "Ana Souza"
    assert perfil.altura_cm == "165"
    assert perfil.meta_semanal == "4"
    assert perfil.tipo_fisico == "Mesomorfo"
    assert perfil.modalidade_fav1 == ["Musculação", "Yoga"]
    assert perfil._medidas is True


def test_carregar_nao_preenche_sem_sessao_verificada(estados):
    perfil, sessao = estados
    sessao.sessao_verificada = False

    asyncio.run(PerfilState.load_profile.fn(perfil))

    assert perfil.nome == ""


def test_salvar_vazio_mostra_erros_sem_chamar_o_xano(estados, chamadas):
    perfil, sessao = estados

    eventos = run_save(perfil)

    assert chamadas["chamadas"] == []
    assert "nome" in perfil.erros and "modalidade_fav1" in perfil.erros
    assert perfil.salvando is False
    assert get_redirects(eventos) == []
    assert sessao.onboarding_concluido is False


def test_salvar_em_onboarding_grava_conclui_e_vai_para_inicio(estados, chamadas):
    perfil, sessao = estados
    asyncio.run(PerfilState.load_profile.fn(perfil))

    eventos = run_save(perfil)

    assert len(chamadas["chamadas"]) == 1
    token, dados = chamadas["chamadas"][0]
    assert token == "tok-123"
    assert dados["medidas"] is True
    assert dados["meta_semanal"] == 4
    assert sessao.onboarding_concluido is True
    assert perfil.salvando is False
    assert has_toast(eventos, "Perfil salvo")
    assert get_redirects(eventos) == ["/inicio"]


def test_salvar_apos_onboarding_permanece_no_perfil(estados, chamadas):
    perfil, sessao = estados
    sessao.onboarding_concluido = True
    asyncio.run(PerfilState.load_profile.fn(perfil))

    eventos = run_save(perfil)

    assert len(chamadas["chamadas"]) == 1
    assert has_toast(eventos, "Perfil salvo")
    assert get_redirects(eventos) == []


def test_falha_do_xano_mostra_mensagem_amigavel_e_mantem_onboarding(estados, chamadas):
    perfil, sessao = estados
    asyncio.run(PerfilState.load_profile.fn(perfil))
    chamadas["resultado"] = XanoError("indisponivel")

    eventos = run_save(perfil)

    assert perfil.erro_geral == MENSAGEM_FALHA_SALVAR
    assert "indisponivel" not in perfil.erro_geral
    assert sessao.onboarding_concluido is False
    assert perfil.salvando is False
    assert get_redirects(eventos) == []


def test_token_rejeitado_encerra_sessao_e_vai_para_login(estados, chamadas):
    perfil, sessao = estados
    asyncio.run(PerfilState.load_profile.fn(perfil))
    chamadas["resultado"] = XanoError("nao_autorizado")

    eventos = run_save(perfil)

    assert sessao.token == ""
    assert get_redirects(eventos) == ["/login"]


def test_duplo_clique_nao_envia_de_novo(estados, chamadas):
    perfil, _ = estados
    asyncio.run(PerfilState.load_profile.fn(perfil))
    perfil.salvando = True

    run_save(perfil)

    assert chamadas["chamadas"] == []


def test_evento_generico_so_altera_campos_do_formulario(estados):
    perfil, _ = estados

    PerfilState.update_field.fn(perfil, "nome", "Bia")
    PerfilState.update_field.fn(perfil, "salvando", "x")
    PerfilState.update_field.fn(perfil, "_medidas", "x")

    assert perfil.nome == "Bia"
    assert perfil.salvando is False
    assert perfil._medidas is False


def test_alternar_modalidade_marca_desmarca_e_limpa_erro(estados):
    perfil, _ = estados
    perfil.erros = {"modalidade_fav1": "Selecione pelo menos uma modalidade."}

    PerfilState.toggle_modalidade.fn(perfil, "Corrida")
    assert perfil.modalidade_fav1 == ["Corrida"]
    assert perfil.erros == {}

    PerfilState.toggle_modalidade.fn(perfil, "Corrida")
    assert perfil.modalidade_fav1 == []
