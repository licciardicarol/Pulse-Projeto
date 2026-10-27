import asyncio

import pytest
from reflex.state import State

import projetofacul.projetofacul  # noqa: F401  registra as páginas e os States
from projetofacul.services import xano_client
from projetofacul.services.xano_client import MENSAGEM_LIMITE_REQUISICOES, XanoError
from projetofacul.states.refeicoes_state import (
    MENSAGEM_FALHA_EXCLUIR,
    MENSAGEM_FALHA_LISTAR,
    MENSAGEM_FALHA_SALVAR,
    RefeicoesState,
)
from projetofacul.states.sessao_state import SessaoState

RELOGIO = {"hoje": "2026-10-21", "hora": 12}


def get_substate(raiz: State, classe):
    return raiz.get_substate(classe.get_full_name().split(".")[1:])


@pytest.fixture
def estados():
    raiz = State(_reflex_internal_init=True)
    refeicoes = get_substate(raiz, RefeicoesState)
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    sessao.sessao_verificada = True
    return refeicoes, sessao


@pytest.fixture
def xano(monkeypatch):
    """Xano simulado com uma lista em memória; `falhas` força erros por função."""
    banco = {"lista": [], "falhas": {}, "chamadas": []}

    async def list_refeicoes(token):
        banco["chamadas"].append(("list", token))
        if "list" in banco["falhas"]:
            raise banco["falhas"]["list"]
        return list(banco["lista"])

    async def create_refeicao(token, data_refeicao, tipo, descricao):
        banco["chamadas"].append(("create", token, data_refeicao, tipo, descricao))
        if "create" in banco["falhas"]:
            raise banco["falhas"]["create"]
        nova = {"id": len(banco["lista"]) + 1, "created_at": len(banco["lista"]) + 1, "data_refeicao": data_refeicao,
                "tipo": tipo, "descricao": descricao, "calorias": 0, "analise_ia": ""}
        banco["lista"].append(nova)
        return nova

    async def delete_refeicao(token, refeicao_id):
        banco["chamadas"].append(("delete", token, refeicao_id))
        if "delete" in banco["falhas"]:
            raise banco["falhas"]["delete"]
        banco["lista"] = [r for r in banco["lista"] if r["id"] != refeicao_id]
        return {"sucesso": True}

    monkeypatch.setattr(xano_client, "list_refeicoes", list_refeicoes)
    monkeypatch.setattr(xano_client, "create_refeicao", create_refeicao)
    monkeypatch.setattr(xano_client, "delete_refeicao", delete_refeicao)
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


def fill(refeicoes, **campos):
    for campo, valor in {"data_refeicao": "2026-10-21", "tipo": "Almoço", "descricao": "Arroz e feijão", **campos}.items():
        RefeicoesState.update_field.fn(refeicoes, campo, valor)


def test_carregar_lista_vazia(estados, xano):
    refeicoes, _ = estados
    run(RefeicoesState.load_meals.fn(refeicoes, RELOGIO))

    assert refeicoes.carregando is False
    assert refeicoes.refeicoes == []
    assert refeicoes.total_calorias == "0"
    assert refeicoes.pendentes_hoje == 0


def test_falha_ao_listar_mostra_erro_amigavel(estados, xano):
    refeicoes, _ = estados
    xano["falhas"]["list"] = XanoError("indisponivel")

    run(RefeicoesState.load_meals.fn(refeicoes, RELOGIO))

    assert refeicoes.erro_lista == MENSAGEM_FALHA_LISTAR
    assert refeicoes.carregando is False


def test_limite_do_xano_ao_listar_pede_para_aguardar(estados, xano):
    refeicoes, _ = estados
    xano["falhas"]["list"] = XanoError("limite_requisicoes")

    run(RefeicoesState.load_meals.fn(refeicoes, RELOGIO))

    assert refeicoes.erro_lista == MENSAGEM_LIMITE_REQUISICOES


def test_abrir_modal_sugere_data_e_tipo(estados):
    refeicoes, _ = estados
    RefeicoesState.open_new_meal.fn(refeicoes)
    RefeicoesState.fill_form_defaults.fn(refeicoes, {"hoje": "2026-10-21", "hora": 8})

    assert refeicoes.modal_aberto is True
    assert refeicoes.data_refeicao == "2026-10-21"
    assert refeicoes.tipo == "Café da manhã"


def test_fechar_modal_mantem_rascunho(estados):
    refeicoes, _ = estados
    fill(refeicoes, descricao="Pão com ovo")
    RefeicoesState.set_modal_open.fn(refeicoes, False)
    RefeicoesState.open_new_meal.fn(refeicoes)
    RefeicoesState.fill_form_defaults.fn(refeicoes, {"hoje": "2026-10-21", "hora": 20})

    assert refeicoes.descricao == "Pão com ovo"
    assert refeicoes.tipo == "Almoço"


def test_salvar_invalido_nao_chama_o_xano(estados, xano):
    refeicoes, _ = estados
    refeicoes.hoje = "2026-10-21"
    fill(refeicoes, descricao="ab", data_refeicao="2026-10-25")

    run(RefeicoesState.save_meal.fn(refeicoes))

    assert [c for c in xano["chamadas"] if c[0] == "create"] == []
    assert "descricao" in refeicoes.erros and "data_refeicao" in refeicoes.erros


def test_salvar_valido_registra_atualiza_e_avisa(estados, xano):
    refeicoes, _ = estados
    refeicoes.hoje = "2026-10-21"
    refeicoes.modal_aberto = True
    fill(refeicoes, descricao="  Arroz, feijão e frango  ")

    eventos = run(RefeicoesState.save_meal.fn(refeicoes))

    assert ("create", "tok-123", "2026-10-21", "Almoço", "Arroz, feijão e frango") in xano["chamadas"]
    assert refeicoes.modal_aberto is False
    assert refeicoes.descricao == "" and refeicoes.data_refeicao == ""
    assert len(refeicoes.refeicoes) == 1
    assert refeicoes.refeicoes[0]["analisada"] == "" and refeicoes.refeicoes[0]["calorias"] == ""
    assert refeicoes.total_calorias == "0"
    assert refeicoes.pendentes_hoje == 1
    assert has_toast(eventos, "Refeição registrada")
    assert refeicoes.salvando is False


def test_falha_ao_salvar_mantem_modal_e_texto(estados, xano):
    refeicoes, _ = estados
    refeicoes.hoje = "2026-10-21"
    refeicoes.modal_aberto = True
    xano["falhas"]["create"] = XanoError("indisponivel")
    fill(refeicoes)

    run(RefeicoesState.save_meal.fn(refeicoes))

    assert refeicoes.erro_geral == MENSAGEM_FALHA_SALVAR
    assert refeicoes.modal_aberto is True
    assert refeicoes.descricao == "Arroz e feijão"
    assert refeicoes.salvando is False


def test_salvar_em_andamento_ignora_segundo_clique(estados, xano):
    refeicoes, _ = estados
    refeicoes.salvando = True
    fill(refeicoes)

    run(RefeicoesState.save_meal.fn(refeicoes))

    assert xano["chamadas"] == []


def test_excluir_confirmado_remove_e_avisa(estados, xano):
    refeicoes, _ = estados
    xano["lista"] = [{"id": 3, "created_at": 1, "data_refeicao": "2026-10-21", "tipo": "Jantar", "descricao": "Sopa", "analise_ia": ""}]
    run(RefeicoesState.load_meals.fn(refeicoes, RELOGIO))

    RefeicoesState.ask_delete.fn(refeicoes, "3")
    eventos = run(RefeicoesState.confirm_delete.fn(refeicoes))

    assert ("delete", "tok-123", 3) in xano["chamadas"]
    assert refeicoes.refeicoes == []
    assert refeicoes.exclusao_id == ""
    assert has_toast(eventos, "Refeição excluída")


def test_cancelar_exclusao_nao_apaga(estados, xano):
    refeicoes, _ = estados
    RefeicoesState.ask_delete.fn(refeicoes, "3")
    RefeicoesState.set_delete_open.fn(refeicoes, False)

    assert refeicoes.exclusao_id == ""
    assert [c for c in xano["chamadas"] if c[0] == "delete"] == []


def test_falha_ao_excluir_mantem_item(estados, xano):
    refeicoes, _ = estados
    xano["lista"] = [{"id": 3, "created_at": 1, "data_refeicao": "2026-10-21", "tipo": "Jantar", "descricao": "Sopa", "analise_ia": ""}]
    run(RefeicoesState.load_meals.fn(refeicoes, RELOGIO))
    xano["falhas"]["delete"] = XanoError("indisponivel")

    RefeicoesState.ask_delete.fn(refeicoes, "3")
    eventos = run(RefeicoesState.confirm_delete.fn(refeicoes))

    assert len(refeicoes.refeicoes) == 1
    assert has_toast(eventos, MENSAGEM_FALHA_EXCLUIR)


def test_sessao_expirada_ao_listar_vai_para_login(estados, xano):
    refeicoes, sessao = estados
    xano["falhas"]["list"] = XanoError("nao_autorizado")

    eventos = run(RefeicoesState.load_meals.fn(refeicoes, RELOGIO))

    assert sessao.token == ""
    assert any("/login" in str(evento) for evento in eventos)
