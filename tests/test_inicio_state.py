import asyncio
import json
import logging
from datetime import datetime

import pytest
from reflex.state import State

import projetofacul.projetofacul  # noqa: F401  registra as páginas e os States
from projetofacul.logic.recomendacao import (
    FIM_REGISTROS,
    INICIO_REGISTROS,
    MENSAGEM_FALHA,
    MENSAGEM_FALHA_REGISTROS,
    MENSAGEM_INDISPONIVEL,
    MENSAGEM_OCUPADA,
)
from projetofacul.logic.sono_registro import to_utc_ms
from projetofacul.services import gemini_client, xano_client
from projetofacul.services.gemini_client import GeminiError
from projetofacul.services.xano_client import XanoError
from projetofacul.states import inicio_state
from projetofacul.states.inicio_state import InicioState
from projetofacul.states.sessao_state import SessaoState

OFFSET = 180
RELOGIO = {"hoje": "2026-11-12", "offset_minutos": OFFSET}


def ms(ano, mes, dia, hora, minuto=0) -> int:
    return to_utc_ms(datetime(ano, mes, dia, hora, minuto), OFFSET)


PERFIL = {"nome": "Carol Teste", "objetivo": "Hipertrofia (ganho de massa muscular)", "nivel_fisico": "Iniciante",
          "modalidade_fav1": ["Musculação"], "meta_semanal": 3, "data_de_nascimento": "2000-01-01"}

SONO_HOJE = {"id": 1, "inicio_sono": ms(2026, 11, 11, 23), "fim_sono": ms(2026, 11, 12, 7), "duracao_minutos": 480,
             "qualidade_sono": 5, "observacoes": "sonhei com a prova"}
TREINO_ONTEM = {"id": 2, "data": "2026-11-11", "nome": "Treino A", "duracao_minutos": 45, "categoria": "Musculação",
                "intensidade": "Leve", "observacoes": ""}
REFEICAO_ANTIGA = {"id": 3, "data_refeicao": "2026-11-01", "tipo": "Jantar", "descricao": "pizza", "calorias": 900,
                   "analise_ia": "pizza"}

RESPOSTA_IA = {
    "titulo": "Dia de acelerar",
    "texto": "Você dormiu 8h e treinou leve ontem.",
    "recuperacao": 82,
    "intensidade": "Intenso",
    "motivo_treino": "Sono excelente e treino leve ontem.",
    "alimentacao": "Sem refeições analisadas ontem e hoje.",
}


def get_substate(raiz: State, classe):
    return raiz.get_substate(classe.get_full_name().split(".")[1:])


@pytest.fixture
def estados():
    raiz = State(_reflex_internal_init=True)
    inicio = get_substate(raiz, InicioState)
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    sessao.sessao_verificada = True
    sessao._perfil = dict(PERFIL)
    return inicio, sessao


@pytest.fixture
def xano(monkeypatch):
    """Xano simulado em memória; `falhas` força erros por função."""
    banco = {"recomendacoes": [], "sono": [SONO_HOJE], "refeicoes": [], "treinos": [TREINO_ONTEM],
             "falhas": {}, "chamadas": []}

    def registrar(nome, *argumentos):
        banco["chamadas"].append((nome, *argumentos))
        if nome in banco["falhas"]:
            raise banco["falhas"][nome]

    async def get_today_recommendation(token, data_recomendacao):
        registrar("hoje", token, data_recomendacao)
        do_dia = [r for r in banco["recomendacoes"] if r["data_recomendacao"] == data_recomendacao]
        return max(do_dia, key=lambda r: r["created_at"]) if do_dia else None

    async def save_recommendation(token, valores):
        registrar("salvar", token, valores)
        nova = {"id": len(banco["recomendacoes"]) + 1, "created_at": ms(2026, 11, 12, 8, 15) + len(banco["recomendacoes"]) * 60000,
                "user_id": 9, **valores}
        banco["recomendacoes"].append(nova)
        return nova

    async def listar(nome, token):
        registrar(nome, token)
        return list(banco[nome])

    monkeypatch.setattr(xano_client, "get_today_recommendation", get_today_recommendation)
    monkeypatch.setattr(xano_client, "save_recommendation", save_recommendation)
    monkeypatch.setattr(xano_client, "list_sono", lambda token: listar("sono", token))
    monkeypatch.setattr(xano_client, "list_refeicoes", lambda token: listar("refeicoes", token))
    monkeypatch.setattr(xano_client, "list_treinos", lambda token: listar("treinos", token))
    return banco


@pytest.fixture
def ia(monkeypatch):
    """Gemini simulado; nada sai para a rede."""
    controle = {"resposta": dict(RESPOSTA_IA), "falha": None, "pedidos": []}

    async def generate_json(instrucao, prompt, esquema, finalidade, max_tokens=1024):
        controle["pedidos"].append(prompt)
        if controle["falha"]:
            raise controle["falha"]
        return controle["resposta"]

    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")
    monkeypatch.setenv("PULSE_ANALISE_SECRET", "segredo-de-teste")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setattr(gemini_client, "generate_json", generate_json)
    monkeypatch.setattr(inicio_state, "get_now_ms", lambda: ms(2026, 11, 12, 9, 40))
    return controle


def run(evento) -> list:
    async def coletar():
        if hasattr(evento, "__aiter__"):
            return [item async for item in evento if item is not None]
        resultado = await evento if asyncio.iscoroutine(evento) else evento
        return [resultado] if resultado is not None else []

    return asyncio.run(coletar())


def pediu_geracao(eventos: list) -> bool:
    return any("generate_recommendation" in str(evento) for evento in eventos)


def abrir(inicio) -> list:
    """Abre o Início como o navegador faria: on_load, relógio e, se pedido, a geração em segundo plano."""
    eventos = run(InicioState.start_page.fn(inicio))
    assert any("call_script" in str(e) or "_call_script" in str(e) for e in eventos)
    eventos = run(InicioState.load_recommendation.fn(inicio, RELOGIO))
    if pediu_geracao(eventos):
        assert inicio.estado in ("preparando", "pronta")
        eventos += run(InicioState.generate_recommendation.fn(inicio))
    return eventos


def atualizar(inicio) -> list:
    eventos = run(InicioState.refresh_recommendation.fn(inicio))
    eventos += run(InicioState.generate_with_clock.fn(inicio, RELOGIO))
    if pediu_geracao(eventos):
        eventos += run(InicioState.generate_recommendation.fn(inicio))
    return eventos


def guardada(dia="2026-11-12", hora=7, **campos) -> dict:
    return {"id": 50, "created_at": ms(2026, 11, int(dia[-2:]), hora), "user_id": 9, "data_recomendacao": dia,
            "titulo": "Guardada", "texto": "Texto guardado.", "recuperacao": 64, "intensidade": "Moderado",
            "motivo_treino": "Motivo guardado.", "alimentacao": "Alimentação guardada.", "modelo": "gemini", **campos}


# ---------- 4.1: carregar, gerar e falhas ----------

def test_recomendacao_de_hoje_existente_e_exibida_sem_chamar_a_ia(estados, xano, ia):
    inicio, _ = estados
    xano["recomendacoes"].append(guardada())

    eventos = abrir(inicio)

    assert not pediu_geracao(eventos)
    assert ia["pedidos"] == []
    assert inicio.estado == "pronta"
    assert inicio.recomendacao["titulo"] == "Guardada"
    assert inicio.recomendacao["recuperacao"] == "64"
    assert inicio.recomendacao["gerada_em"] == "Gerada às 07:00"
    assert ("hoje", "tok-123", "2026-11-12") in xano["chamadas"]
    # só a busca da recomendação: nenhum registro é listado
    assert [c[0] for c in xano["chamadas"]] == ["hoje"]


def test_sem_a_de_hoje_gera_guarda_e_exibe(estados, xano, ia):
    inicio, _ = estados

    abrir(inicio)

    assert len(ia["pedidos"]) == 1
    salvar = [c for c in xano["chamadas"] if c[0] == "salvar"]
    assert salvar == [("salvar", "tok-123", {
        "data_recomendacao": "2026-11-12", **RESPOSTA_IA, "modelo": "gemini-3.5-flash-lite",
    })]
    assert inicio.estado == "pronta"
    assert inicio.recomendacao == {
        "titulo": "Dia de acelerar",
        "texto": RESPOSTA_IA["texto"],
        "recuperacao": "82",
        "recuperacao_rotulo": "Recuperação estimada: 82 de 100",
        "intensidade": "Intenso",
        "motivo_treino": RESPOSTA_IA["motivo_treino"],
        "alimentacao": RESPOSTA_IA["alimentacao"],
        "gerada_em": "Gerada às 08:15",
    }
    assert inicio.mensagem_erro == ""
    assert inicio._gerando is False


def test_pedido_leva_os_registros_e_nao_o_nome_nem_as_observacoes(estados, xano, ia):
    inicio, _ = estados

    abrir(inicio)

    prompt = ia["pedidos"][0]
    contexto = json.loads(prompt.split(INICIO_REGISTROS + "\n")[1].split("\n" + FIM_REGISTROS)[0])
    assert contexto["data_hoje"] == "2026-11-12"
    assert contexto["sono_ultimos_7_dias"]["noites"][0]["duracao_minutos"] == 480
    assert contexto["treinos_ultimos_7_dias"][0]["nome"] == "Treino A"
    assert "Carol Teste" not in prompt
    assert "sonhei com a prova" not in prompt
    assert "tok-123" not in prompt


def test_segunda_visita_no_mesmo_dia_nao_gera_de_novo(estados, xano, ia):
    inicio, _ = estados
    abrir(inicio)

    abrir(inicio)

    assert len(ia["pedidos"]) == 1
    assert inicio.recomendacao["titulo"] == "Dia de acelerar"


def test_recomendacao_de_ontem_nao_e_reaproveitada(estados, xano, ia):
    inicio, _ = estados
    xano["recomendacoes"].append(guardada(dia="2026-11-11"))

    abrir(inicio)

    assert len(ia["pedidos"]) == 1
    assert inicio.recomendacao["titulo"] == "Dia de acelerar"


@pytest.mark.parametrize(
    "registros",
    [
        {"sono": [], "refeicoes": [], "treinos": []},
        {"sono": [], "refeicoes": [REFEICAO_ANTIGA], "treinos": []},
    ],
)
def test_sem_registros_recentes_mostra_convite_sem_ia(estados, xano, ia, registros):
    inicio, _ = estados
    xano.update(registros)

    abrir(inicio)

    assert inicio.estado == "sem_dados"
    assert ia["pedidos"] == []
    assert not [c for c in xano["chamadas"] if c[0] == "salvar"]
    assert inicio.recomendacao == {}


@pytest.mark.parametrize("variavel", ["GEMINI_API_KEY", "PULSE_ANALISE_SECRET"])
def test_sem_configuracao_mostra_indisponivel_sem_ia(estados, xano, ia, monkeypatch, caplog, variavel):
    inicio, _ = estados
    monkeypatch.delenv(variavel)

    with caplog.at_level(logging.WARNING):
        abrir(inicio)

    assert inicio.estado == "erro"
    assert inicio.mensagem_erro == MENSAGEM_INDISPONIVEL
    assert ia["pedidos"] == []
    # o log diz o nome do que falta, nunca o valor
    assert variavel in caplog.text
    assert "chave-de-teste" not in caplog.text and "segredo-de-teste" not in caplog.text


def test_sem_configuracao_e_sem_registros_mostra_o_convite(estados, xano, ia, monkeypatch):
    inicio, _ = estados
    monkeypatch.delenv("GEMINI_API_KEY")
    xano.update({"sono": [], "treinos": []})

    abrir(inicio)

    assert inicio.estado == "sem_dados"


@pytest.mark.parametrize(
    ("ajuste", "mensagem"),
    [
        ({"falha": GeminiError("limite_requisicoes")}, MENSAGEM_OCUPADA),
        ({"falha": GeminiError("sobrecarregado")}, MENSAGEM_OCUPADA),
        ({"falha": GeminiError("falha")}, MENSAGEM_FALHA),
        ({"resposta": {**RESPOSTA_IA, "intensidade": "Muito forte"}}, MENSAGEM_FALHA),
        ({"resposta": {**RESPOSTA_IA, "recuperacao": 140}}, MENSAGEM_FALHA),
        ({"resposta": "isto não é um objeto"}, MENSAGEM_FALHA),
    ],
)
def test_falhas_da_ia_nao_guardam_e_mostram_mensagem(estados, xano, ia, ajuste, mensagem):
    inicio, _ = estados
    ia.update(ajuste)

    abrir(inicio)

    assert inicio.estado == "erro"
    assert inicio.mensagem_erro == mensagem
    assert not [c for c in xano["chamadas"] if c[0] == "salvar"]
    assert inicio._gerando is False


def test_falha_ao_guardar_ainda_exibe_a_recomendacao(estados, xano, ia):
    inicio, _ = estados
    xano["falhas"]["salvar"] = XanoError("indisponivel")

    abrir(inicio)

    assert inicio.estado == "pronta"
    assert inicio.recomendacao["titulo"] == "Dia de acelerar"
    # sem created_at do Xano, o horário é o de agora
    assert inicio.recomendacao["gerada_em"] == "Gerada às 09:40"
    assert xano["recomendacoes"] == []


@pytest.mark.parametrize("onde", ["hoje", "sono", "salvar"])
def test_sessao_expirada_vai_para_o_login(estados, xano, ia, onde):
    inicio, sessao = estados
    xano["falhas"][onde] = XanoError("nao_autorizado")

    eventos = abrir(inicio)

    assert sessao.token == ""
    assert any("/login" in str(evento) for evento in eventos)


@pytest.mark.parametrize("onde", ["hoje", "refeicoes", "treinos"])
def test_falha_ao_carregar_registros(estados, xano, ia, onde):
    inicio, _ = estados
    xano["falhas"][onde] = XanoError("indisponivel")

    abrir(inicio)

    assert inicio.estado == "erro"
    assert inicio.mensagem_erro == MENSAGEM_FALHA_REGISTROS
    assert ia["pedidos"] == []


def test_sem_sessao_verificada_nao_carrega_nada(estados, xano, ia):
    inicio, sessao = estados
    sessao.sessao_verificada = False

    assert run(InicioState.start_page.fn(inicio)) == []
    assert xano["chamadas"] == []


def test_tentar_novamente_refaz_o_carregamento(estados, xano, ia):
    inicio, _ = estados
    ia["falha"] = GeminiError("falha")
    abrir(inicio)
    assert inicio.estado == "erro"

    ia["falha"] = None
    abrir(inicio)

    assert inicio.estado == "pronta"
    assert inicio.mensagem_erro == ""


# ---------- 4.2: Atualizar ----------

def test_atualizar_gera_guarda_e_troca_o_horario(estados, xano, ia):
    inicio, _ = estados
    xano["recomendacoes"].append(guardada())
    abrir(inicio)
    assert inicio.recomendacao["gerada_em"] == "Gerada às 07:00"

    atualizar(inicio)

    assert len(ia["pedidos"]) == 1
    assert len(xano["recomendacoes"]) == 2  # a anterior continua no histórico
    assert inicio.recomendacao["titulo"] == "Dia de acelerar"
    # o Xano simulado grava a segunda linha 1 minuto depois da primeira
    assert inicio.recomendacao["gerada_em"] == "Gerada às 08:16"
    assert inicio.atualizando is False


def test_atualizar_usa_a_noite_recem_registrada(estados, xano, ia):
    inicio, _ = estados
    xano["sono"] = []
    xano["recomendacoes"].append(guardada())
    abrir(inicio)

    xano["sono"] = [{**SONO_HOJE, "duracao_minutos": 333}]
    atualizar(inicio)

    assert '"duracao_minutos": 333' in ia["pedidos"][0]


def test_durante_a_atualizacao_a_anterior_continua_na_tela(estados, xano, ia):
    inicio, _ = estados
    xano["recomendacoes"].append(guardada())
    abrir(inicio)

    run(InicioState.refresh_recommendation.fn(inicio))
    eventos = run(InicioState.generate_with_clock.fn(inicio, RELOGIO))

    assert pediu_geracao(eventos)
    assert inicio.atualizando is True
    assert inicio.estado == "pronta"
    assert inicio.recomendacao["titulo"] == "Guardada"


def test_clique_duplo_em_atualizar_chama_a_ia_uma_vez(estados, xano, ia):
    inicio, _ = estados
    xano["recomendacoes"].append(guardada())
    abrir(inicio)

    run(InicioState.refresh_recommendation.fn(inicio))
    run(InicioState.refresh_recommendation.fn(inicio))
    primeiro = run(InicioState.generate_with_clock.fn(inicio, RELOGIO))
    segundo = run(InicioState.generate_with_clock.fn(inicio, RELOGIO))
    # com a geração em andamento, um terceiro clique nem pede o relógio
    assert run(InicioState.refresh_recommendation.fn(inicio)) == []
    run(InicioState.generate_recommendation.fn(inicio))
    # um evento repetido que chegue depois encontra a trava desligada e não faz nada
    run(InicioState.generate_recommendation.fn(inicio))

    assert pediu_geracao(primeiro)
    assert segundo == []
    assert len(ia["pedidos"]) == 1


def test_atualizar_que_falha_mantem_a_anterior_com_a_mensagem(estados, xano, ia):
    inicio, _ = estados
    xano["recomendacoes"].append(guardada())
    abrir(inicio)
    ia["falha"] = GeminiError("sobrecarregado")

    atualizar(inicio)

    assert inicio.estado == "pronta"
    assert inicio.recomendacao["titulo"] == "Guardada"
    assert inicio.mensagem_erro == MENSAGEM_OCUPADA
    assert inicio.atualizando is False
    assert len(xano["recomendacoes"]) == 1


def test_atualizar_de_novo_limpa_a_mensagem_anterior(estados, xano, ia):
    inicio, _ = estados
    xano["recomendacoes"].append(guardada())
    abrir(inicio)
    ia["falha"] = GeminiError("falha")
    atualizar(inicio)

    ia["falha"] = None
    run(InicioState.refresh_recommendation.fn(inicio))
    run(InicioState.generate_with_clock.fn(inicio, RELOGIO))
    assert inicio.mensagem_erro == ""
    run(InicioState.generate_recommendation.fn(inicio))

    assert inicio.recomendacao["titulo"] == "Dia de acelerar"
