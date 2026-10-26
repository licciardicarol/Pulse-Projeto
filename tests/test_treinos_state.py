import asyncio
from datetime import date

import pytest
from reflex.state import State

import projetofacul.projetofacul  # noqa: F401  registra as páginas e os States
from projetofacul.services import xano_client
from projetofacul.services.xano_client import MENSAGEM_LIMITE_REQUISICOES, XanoError
from projetofacul.states import treinos_state
from projetofacul.states.sessao_state import SessaoState
from projetofacul.states.treinos_state import (
    MENSAGEM_FALHA_EXCLUIR,
    MENSAGEM_FALHA_LISTAR,
    MENSAGEM_FALHA_SALVAR,
    TreinosState,
)

HOJE = date(2026, 10, 26)


def get_substate(raiz: State, classe):
    return raiz.get_substate(classe.get_full_name().split(".")[1:])


@pytest.fixture
def estados(monkeypatch):
    # "hoje" fixo em São Paulo, independente do relógio da máquina
    monkeypatch.setattr(treinos_state, "get_today_sao_paulo", lambda: HOJE)
    raiz = State(_reflex_internal_init=True)
    treinos = get_substate(raiz, TreinosState)
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    sessao.sessao_verificada = True
    return treinos, sessao


@pytest.fixture
def xano(monkeypatch):
    """Xano simulado com uma lista em memória; `falhas` força erros por função."""
    banco = {"lista": [], "falhas": {}, "chamadas": []}

    async def list_treinos(token):
        banco["chamadas"].append(("list", token))
        if "list" in banco["falhas"]:
            raise banco["falhas"]["list"]
        return list(banco["lista"])

    async def create_treino(token, dados):
        banco["chamadas"].append(("create", token, dados))
        if "create" in banco["falhas"]:
            raise banco["falhas"]["create"]
        novo = {"id": len(banco["lista"]) + 1, "user_id": 35, **dados}
        banco["lista"].append(novo)
        return novo

    async def delete_treino(token, treino_id):
        banco["chamadas"].append(("delete", token, treino_id))
        if "delete" in banco["falhas"]:
            raise banco["falhas"]["delete"]
        banco["lista"] = [t for t in banco["lista"] if t["id"] != treino_id]
        return {"sucesso": True}

    monkeypatch.setattr(xano_client, "list_treinos", list_treinos)
    monkeypatch.setattr(xano_client, "create_treino", create_treino)
    monkeypatch.setattr(xano_client, "delete_treino", delete_treino)
    return banco


def run(evento) -> list:
    async def coletar():
        if hasattr(evento, "__aiter__"):
            return [item async for item in evento if item is not None]
        resultado = await evento if asyncio.iscoroutine(evento) else evento
        return [resultado] if resultado is not None else []

    return asyncio.run(coletar())


def has_toast(eventos: list, texto: str) -> bool:
    return any("__toast" in str(evento) and texto in str(evento) for evento in eventos)


def fill(treinos, **campos):
    for campo, valor in {"data": "2026-10-26", "duracao_minutos": "60", "nome": "Peito e tríceps", **campos}.items():
        TreinosState.update_field.fn(treinos, campo, valor)


def test_carregar_lista_vazia(estados, xano):
    treinos, _ = estados
    run(TreinosState.start_page.fn(treinos))

    assert treinos.carregando is False
    assert treinos.treinos == []
    assert treinos.erro_lista == ""
    assert treinos.hoje == "2026-10-26"


def test_lista_ordenada_e_sem_opcionais_inventados(estados, xano):
    treinos, _ = estados
    xano["lista"] = [
        {"id": 1, "data": "2026-10-25", "duracao_minutos": 30, "nome": "Corrida", "categoria": "Corrida"},
        {"id": 2, "data": "2026-10-26", "duracao_minutos": 60, "nome": "Perna", "categoria": None},
    ]

    run(TreinosState.start_page.fn(treinos))

    assert [t["nome"] for t in treinos.treinos] == ["Perna", "Corrida"]
    assert treinos.treinos[0]["categoria"] == ""
    assert treinos.treinos[0]["duracao"] == "60 min"


def test_sem_sessao_verificada_nao_chama_o_xano(estados, xano):
    treinos, sessao = estados
    sessao.sessao_verificada = False

    run(TreinosState.start_page.fn(treinos))

    assert xano["chamadas"] == []


def test_falha_ao_listar_mostra_erro_amigavel(estados, xano):
    treinos, _ = estados
    xano["falhas"]["list"] = XanoError("indisponivel")

    run(TreinosState.start_page.fn(treinos))

    assert treinos.erro_lista == MENSAGEM_FALHA_LISTAR
    assert treinos.carregando is False


def test_limite_do_xano_ao_listar_pede_para_aguardar(estados, xano):
    treinos, _ = estados
    xano["falhas"]["list"] = XanoError("limite_requisicoes")

    run(TreinosState.start_page.fn(treinos))

    assert treinos.erro_lista == MENSAGEM_LIMITE_REQUISICOES


def test_sessao_expirada_ao_listar_vai_para_login(estados, xano):
    treinos, sessao = estados
    xano["falhas"]["list"] = XanoError("nao_autorizado")

    eventos = run(TreinosState.start_page.fn(treinos))

    assert sessao.token == ""
    assert any("/login" in str(evento) for evento in eventos)


def test_abrir_modal_preenche_data_de_hoje_e_mantem_rascunho(estados):
    treinos, _ = estados
    TreinosState.open_new_workout.fn(treinos)

    assert treinos.modal_aberto is True
    assert treinos.data == "2026-10-26"
    assert treinos.duracao_minutos == ""

    TreinosState.update_field.fn(treinos, "nome", "Costas")
    TreinosState.update_field.fn(treinos, "data", "2026-10-20")
    TreinosState.set_modal_open.fn(treinos, False)
    TreinosState.open_new_workout.fn(treinos)

    assert treinos.nome == "Costas"
    assert treinos.data == "2026-10-20"


def test_campo_desconhecido_e_ignorado(estados):
    treinos, _ = estados
    TreinosState.update_field.fn(treinos, "user_id", "36")

    assert not hasattr(treinos, "user_id") or treinos.user_id != "36"


def test_validacao_nao_chama_o_xano(estados, xano):
    treinos, _ = estados
    fill(treinos, duracao_minutos="0", nome="a", data="2026-10-27")

    run(TreinosState.save_workout.fn(treinos))

    assert set(treinos.erros) == {"duracao_minutos", "nome", "data"}
    assert xano["chamadas"] == []


def test_corrigir_campo_limpa_o_erro_dele(estados, xano):
    treinos, _ = estados
    fill(treinos, nome="a")
    run(TreinosState.save_workout.fn(treinos))
    TreinosState.update_field.fn(treinos, "nome", "Perna")

    assert "nome" not in treinos.erros


def test_salvar_com_sucesso(estados, xano):
    treinos, _ = estados
    TreinosState.open_new_workout.fn(treinos)
    fill(treinos, categoria="Musculação", intensidade="Alta")

    eventos = run(TreinosState.save_workout.fn(treinos))

    assert xano["chamadas"][0] == ("create", "tok-123", {"data": "2026-10-26", "duracao_minutos": 60,
                                                         "nome": "Peito e tríceps", "categoria": "Musculação",
                                                         "intensidade": "Alta"})
    assert treinos.modal_aberto is False
    assert treinos.salvando is False
    assert treinos.nome == "" and treinos.data == ""
    assert [t["nome"] for t in treinos.treinos] == ["Peito e tríceps"]
    assert has_toast(eventos, "Treino registrado")


def test_duplo_clique_cria_um_treino_so(estados, xano):
    treinos, _ = estados
    fill(treinos)
    treinos.salvando = True

    run(TreinosState.save_workout.fn(treinos))

    assert xano["chamadas"] == []


def test_falha_ao_salvar_mantem_modal_e_dados(estados, xano):
    treinos, _ = estados
    TreinosState.open_new_workout.fn(treinos)
    fill(treinos)
    xano["falhas"]["create"] = XanoError("indisponivel")

    eventos = run(TreinosState.save_workout.fn(treinos))

    assert treinos.erro_geral == MENSAGEM_FALHA_SALVAR
    assert treinos.modal_aberto is True
    assert treinos.nome == "Peito e tríceps"
    assert treinos.salvando is False
    assert not has_toast(eventos, "Treino registrado")


def test_nao_fecha_o_modal_durante_o_salvamento(estados):
    treinos, _ = estados
    treinos.modal_aberto = True
    treinos.salvando = True

    TreinosState.set_modal_open.fn(treinos, False)

    assert treinos.modal_aberto is True


def test_cancelar_exclusao_nao_apaga(estados, xano):
    treinos, _ = estados
    xano["lista"] = [{"id": 1, "data": "2026-10-26", "duracao_minutos": 60, "nome": "Perna"}]
    TreinosState.ask_delete.fn(treinos, "1", "Perna")
    TreinosState.set_delete_open.fn(treinos, False)

    assert treinos.exclusao_id == ""
    assert treinos.exclusao_nome == ""
    assert xano["chamadas"] == []


def test_confirmar_exclusao(estados, xano):
    treinos, _ = estados
    xano["lista"] = [{"id": 1, "data": "2026-10-26", "duracao_minutos": 60, "nome": "Perna"}]
    run(TreinosState.start_page.fn(treinos))
    TreinosState.ask_delete.fn(treinos, "1", "Perna")

    eventos = run(TreinosState.confirm_delete.fn(treinos))

    assert ("delete", "tok-123", 1) in xano["chamadas"]
    assert treinos.treinos == []
    assert treinos.exclusao_id == ""
    assert has_toast(eventos, "Treino excluído")


def test_falha_ao_excluir_mantem_o_item(estados, xano):
    treinos, _ = estados
    xano["lista"] = [{"id": 1, "data": "2026-10-26", "duracao_minutos": 60, "nome": "Perna"}]
    run(TreinosState.start_page.fn(treinos))
    TreinosState.ask_delete.fn(treinos, "1", "Perna")
    xano["falhas"]["delete"] = XanoError("indisponivel")

    eventos = run(TreinosState.confirm_delete.fn(treinos))

    assert len(treinos.treinos) == 1
    assert has_toast(eventos, MENSAGEM_FALHA_EXCLUIR)
