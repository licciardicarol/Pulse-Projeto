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


# ---------- análise por IA ----------

from projetofacul.logic.analise_refeicao import (  # noqa: E402
    MENSAGEM_FALHA_ANALISE,
    MENSAGEM_IA_INDISPONIVEL,
    MENSAGEM_LIMITE_IA,
    MENSAGEM_NAO_RECONHECIDO,
)
from projetofacul.services import gemini_client  # noqa: E402
from projetofacul.services.gemini_client import GeminiError  # noqa: E402

RESPOSTA_IA = {
    "reconhecido": True,
    "resumo": "2 ovos (~140 kcal), 1 pão francês (~135 kcal)",
    "calorias": 275.36,
    "proteinas": 16.04,
    "carboidratos": 29.9,
    "gorduras": 10.55,
}


@pytest.fixture
def ia(monkeypatch, xano):
    """Gemini e gravação da análise simulados; nada sai para a rede."""
    controle = {"resposta": dict(RESPOSTA_IA), "falha_ia": None, "falha_gravar": None, "pedidos": [], "gravacoes": []}

    async def analyze_meal(tipo, descricao):
        controle["pedidos"].append((tipo, descricao))
        if controle["falha_ia"]:
            raise controle["falha_ia"]
        return controle["resposta"]

    async def save_meal_analysis(token, refeicao_id, valores):
        controle["gravacoes"].append((token, refeicao_id, valores))
        if controle["falha_gravar"]:
            raise controle["falha_gravar"]
        for item in xano["lista"]:
            if item["id"] == refeicao_id:
                item.update(valores)
                return dict(item)
        raise XanoError("nao_encontrado")

    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")
    monkeypatch.setenv("PULSE_ANALISE_SECRET", "segredo-de-teste")
    monkeypatch.setattr(gemini_client, "analyze_meal", analyze_meal)
    monkeypatch.setattr(xano_client, "save_meal_analysis", save_meal_analysis)
    return controle


def pendente(id_=1, dia="2026-10-21", descricao="2 ovos mexidos e 1 pão francês") -> dict:
    return {"id": id_, "created_at": id_, "data_refeicao": dia, "tipo": "Café da manhã", "descricao": descricao,
            "calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, "analise_ia": ""}


def load(refeicoes, xano, *lista):
    xano["lista"] = [dict(item) for item in lista]
    run(RefeicoesState.load_meals.fn(refeicoes, RELOGIO))


def analyze(refeicoes, refeicao_id="1") -> list:
    return run(RefeicoesState.analyze_meal.fn(refeicoes, refeicao_id))


def chamou_analise(eventos: list) -> bool:
    return any("analyze_meal" in str(evento) for evento in eventos)


def test_salvar_dispara_analise_em_segundo_plano_e_mostra_analisando(estados, xano, ia):
    refeicoes, _ = estados
    refeicoes.hoje = "2026-10-21"
    fill(refeicoes, descricao="2 ovos mexidos e 1 pão francês")

    eventos = run(RefeicoesState.save_meal.fn(refeicoes))

    assert has_toast(eventos, "Refeição registrada")
    assert chamou_analise(eventos)
    assert refeicoes.modal_aberto is False
    assert refeicoes.refeicoes[0]["estado"] == "analisando"
    # o registro não esperou pela IA
    assert ia["pedidos"] == []


def test_analise_valida_grava_e_atualiza_totais_sem_nova_listagem(estados, xano, ia):
    refeicoes, _ = estados
    load(refeicoes, xano, pendente())
    listagens = len([c for c in xano["chamadas"] if c[0] == "list"])

    assert chamou_analise([RefeicoesState.request_analysis.fn(refeicoes, "1")])
    analyze(refeicoes)

    assert ia["pedidos"] == [("Café da manhã", "2 ovos mexidos e 1 pão francês")]
    assert ia["gravacoes"] == [("tok-123", 1, {"calorias": 275.4, "proteinas": 16.0, "carboidratos": 29.9,
                                               "gorduras": 10.6, "analise_ia": RESPOSTA_IA["resumo"]})]
    assert len([c for c in xano["chamadas"] if c[0] == "list"]) == listagens
    item = refeicoes.refeicoes[0]
    assert item["estado"] == "analisada"
    assert item["calorias"] == "275,4 kcal"
    assert item["resumo"] == RESPOSTA_IA["resumo"]
    assert refeicoes.total_calorias == "275,4"
    assert refeicoes.total_proteinas == "16"
    assert refeicoes.total_gorduras == "10,6"
    assert refeicoes.pendentes_hoje == 0


@pytest.mark.parametrize(
    ("ajuste", "mensagem", "gravou"),
    [
        ({"falha_ia": GeminiError("limite_requisicoes")}, MENSAGEM_LIMITE_IA, False),
        ({"falha_ia": GeminiError("falha")}, MENSAGEM_FALHA_ANALISE, False),
        ({"falha_ia": GeminiError("nao_configurado")}, MENSAGEM_IA_INDISPONIVEL, False),
        ({"resposta": {**RESPOSTA_IA, "calorias": 12000}}, MENSAGEM_FALHA_ANALISE, False),
        ({"resposta": "isto não é um objeto"}, MENSAGEM_FALHA_ANALISE, False),
        ({"resposta": {"reconhecido": False, "resumo": "", "calorias": 0, "proteinas": 0, "carboidratos": 0,
                       "gorduras": 0}}, MENSAGEM_NAO_RECONHECIDO, False),
        ({"falha_gravar": XanoError("acesso_negado")}, MENSAGEM_FALHA_ANALISE, True),
        ({"falha_gravar": XanoError("limite_requisicoes")}, MENSAGEM_FALHA_ANALISE, True),
    ],
)
def test_falhas_da_analise_deixam_mensagem_sem_valores(estados, xano, ia, ajuste, mensagem, gravou):
    refeicoes, _ = estados
    load(refeicoes, xano, pendente())
    ia.update(ajuste)

    RefeicoesState.request_analysis.fn(refeicoes, "1")
    analyze(refeicoes)

    item = refeicoes.refeicoes[0]
    assert item["estado"] == "pendente"
    assert item["erro_analise"] == mensagem
    assert item["calorias"] == ""
    assert refeicoes.total_calorias == "0"
    assert refeicoes.pendentes_hoje == 1
    assert bool(ia["gravacoes"]) is gravou


def test_tentar_de_novo_limpa_a_falha_anterior(estados, xano, ia):
    refeicoes, _ = estados
    load(refeicoes, xano, pendente())
    ia["falha_ia"] = GeminiError("falha")
    RefeicoesState.request_analysis.fn(refeicoes, "1")
    analyze(refeicoes)

    ia["falha_ia"] = None
    RefeicoesState.request_analysis.fn(refeicoes, "1")
    assert refeicoes.refeicoes[0]["estado"] == "analisando"
    assert refeicoes.refeicoes[0]["erro_analise"] == ""
    analyze(refeicoes)

    assert refeicoes.refeicoes[0]["estado"] == "analisada"


def test_clique_duplo_chama_a_ia_uma_vez(estados, xano, ia):
    refeicoes, _ = estados
    load(refeicoes, xano, pendente())

    primeiro = RefeicoesState.request_analysis.fn(refeicoes, "1")
    segundo = RefeicoesState.request_analysis.fn(refeicoes, "1")
    analyze(refeicoes)
    # um evento de análise repetido que chegue depois não encontra mais o id em andamento
    analyze(refeicoes)

    assert chamou_analise([primeiro])
    assert segundo is None
    assert len(ia["pedidos"]) == 1


def test_refeicao_ja_analisada_nao_vai_para_a_ia(estados, xano, ia):
    refeicoes, _ = estados
    load(refeicoes, xano, {**pendente(), "analise_ia": "2 ovos", "calorias": 140})

    assert RefeicoesState.request_analysis.fn(refeicoes, "1") is None
    assert ia["pedidos"] == []


def test_sem_configuracao_registra_mas_nao_chama_a_ia(estados, xano, ia, monkeypatch):
    refeicoes, _ = estados
    monkeypatch.delenv("GEMINI_API_KEY")
    refeicoes.hoje = "2026-10-21"
    fill(refeicoes)

    eventos = run(RefeicoesState.save_meal.fn(refeicoes))

    assert has_toast(eventos, "Refeição registrada")
    assert not chamou_analise(eventos)
    assert ia["pedidos"] == []
    assert refeicoes.refeicoes[0]["estado"] == "pendente"
    assert refeicoes.refeicoes[0]["erro_analise"] == MENSAGEM_IA_INDISPONIVEL


def test_sem_chave_de_servico_tambem_nao_chama_a_ia(estados, xano, ia, monkeypatch):
    refeicoes, _ = estados
    monkeypatch.delenv("PULSE_ANALISE_SECRET")
    load(refeicoes, xano, pendente())

    assert RefeicoesState.request_analysis.fn(refeicoes, "1") is None
    assert ia["pedidos"] == []
    assert refeicoes.refeicoes[0]["erro_analise"] == MENSAGEM_IA_INDISPONIVEL


def test_sessao_expirada_ao_gravar_vai_para_login(estados, xano, ia):
    refeicoes, sessao = estados
    load(refeicoes, xano, pendente())
    ia["falha_gravar"] = XanoError("nao_autorizado")

    RefeicoesState.request_analysis.fn(refeicoes, "1")
    eventos = analyze(refeicoes)

    assert sessao.token == ""
    assert any("/login" in str(evento) for evento in eventos)


def test_falha_ao_registrar_nao_chama_a_ia(estados, xano, ia):
    refeicoes, _ = estados
    refeicoes.hoje = "2026-10-21"
    refeicoes.modal_aberto = True
    xano["falhas"]["create"] = XanoError("indisponivel")
    fill(refeicoes)

    eventos = run(RefeicoesState.save_meal.fn(refeicoes))

    assert not chamou_analise(eventos)
    assert ia["pedidos"] == []
    assert refeicoes.modal_aberto is True


def test_abrir_a_pagina_nao_chama_a_ia(estados, xano, ia):
    refeicoes, _ = estados

    load(refeicoes, xano, pendente(1), pendente(2, descricao="arroz e feijão"))

    assert ia["pedidos"] == []
    assert [item["estado"] for item in refeicoes.refeicoes] == ["pendente", "pendente"]


def test_refeicao_excluida_durante_a_analise_nao_deixa_rastro(estados, xano, ia):
    refeicoes, _ = estados
    load(refeicoes, xano, pendente())
    ia["falha_gravar"] = XanoError("nao_encontrado")
    RefeicoesState.request_analysis.fn(refeicoes, "1")

    # o usuário exclui a refeição enquanto a IA responde
    xano["lista"] = []
    run(RefeicoesState.load_meals.fn(refeicoes, RELOGIO))
    analyze(refeicoes)

    assert refeicoes.refeicoes == []
    assert refeicoes._erros_analise == {}
    assert refeicoes._analisando == []
