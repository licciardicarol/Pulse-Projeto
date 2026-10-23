import re
from datetime import date
from pathlib import Path

import pytest

from projetofacul.logic.refeicoes import (
    OPCOES_TIPO,
    build_meal_view,
    build_refeicao_payload,
    calculate_daily_totals,
    count_pending_today,
    format_date_br,
    format_number,
    is_analyzed,
    sort_refeicoes,
    suggest_meal_type,
    validate_refeicao,
)

HOJE = date(2026, 10, 21)
RAIZ = Path(__file__).resolve().parent.parent


def dados(**alteracoes):
    return {"data_refeicao": "2026-10-21", "tipo": "Almoço", "descricao": "Arroz, feijão e frango", **alteracoes}


def refeicao(id_, dia, criada, analise="", **valores):
    return {"id": id_, "data_refeicao": dia, "created_at": criada, "analise_ia": analise, "tipo": "Almoço",
            "descricao": "x", "calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, **valores}


def test_tipos_iguais_ao_enum_do_xano():
    conteudo = (RAIZ / "xano" / "table" / "refeicoes.xs").read_text(encoding="utf-8")
    bloco = re.search(r"enum tipo\??\s*\{\s*values\s*=\s*\[(.*?)\]", conteudo, re.DOTALL).group(1)
    assert set(re.findall(r'"([^"]+)"', bloco)) == set(OPCOES_TIPO)
    assert OPCOES_TIPO == ("Café da manhã", "Almoço", "Café da tarde", "Jantar")


@pytest.mark.parametrize(
    ("hora", "tipo"),
    [(5, "Café da manhã"), (10, "Café da manhã"), (11, "Almoço"), (14, "Almoço"), (15, "Café da tarde"),
     (17, "Café da tarde"), (18, "Jantar"), (23, "Jantar"), (0, "Jantar"), (4, "Jantar")],
)
def test_tipo_sugerido_pelo_horario(hora, tipo):
    assert suggest_meal_type(hora) == tipo


def test_refeicao_valida_nao_tem_erros():
    assert validate_refeicao(dados(), HOJE) == {}
    assert validate_refeicao(dados(descricao="abc"), HOJE) == {}
    assert validate_refeicao(dados(descricao="x" * 500), HOJE) == {}
    assert validate_refeicao(dados(data_refeicao="2026-10-20"), HOJE) == {}


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("descricao", ""), ("descricao", "  ab  "), ("descricao", "x" * 501), ("data_refeicao", ""),
     ("data_refeicao", "21/10/2026"), ("data_refeicao", "2026-10-22"), ("tipo", ""), ("tipo", "Lanche"),
     ("tipo", "Pré-treino")],
)
def test_campos_invalidos_geram_erro(campo, valor):
    assert campo in validate_refeicao(dados(**{campo: valor}), HOJE)


def test_payload_envia_so_data_tipo_e_descricao():
    payload = build_refeicao_payload({**dados(descricao="  Sopa  "), "calorias": "500", "user_id": "9"})
    assert payload == {"data_refeicao": "2026-10-21", "tipo": "Almoço", "descricao": "Sopa"}


def test_analisada_depende_so_da_analise_ia():
    assert not is_analyzed(refeicao(1, "2026-10-21", 1, calorias=300))
    assert not is_analyzed({"analise_ia": None})
    assert not is_analyzed({"analise_ia": "   "})
    assert is_analyzed(refeicao(1, "2026-10-21", 1, analise="Refeição equilibrada"))


def test_ordena_mais_recentes_primeiro():
    lista = [refeicao(1, "2026-10-20", 100), refeicao(2, "2026-10-21", 50), refeicao(3, "2026-10-21", 90)]
    assert [r["id"] for r in sort_refeicoes(lista)] == [3, 2, 1]


def test_totais_somam_so_hoje_e_analisadas():
    lista = [
        refeicao(1, "2026-10-21", 1, analise="ok", calorias=400, proteinas=30, carboidratos=50, gorduras=10.5),
        refeicao(2, "2026-10-21", 2, analise="ok", calorias=250.5, proteinas=12, carboidratos=20, gorduras=8),
        refeicao(3, "2026-10-21", 3, calorias=999, proteinas=99),  # aguardando análise: não soma
        refeicao(4, "2026-10-20", 4, analise="ok", calorias=800, proteinas=40),  # ontem: não soma
    ]
    assert calculate_daily_totals(lista, HOJE) == {"calorias": 650.5, "proteinas": 42, "carboidratos": 70, "gorduras": 18.5}
    assert count_pending_today(lista, HOJE) == 1


def test_sem_refeicoes_analisadas_totais_ficam_zero():
    lista = [refeicao(1, "2026-10-21", 1), refeicao(2, "2026-10-21", 2)]
    assert calculate_daily_totals(lista, HOJE) == {"calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0}
    assert count_pending_today(lista, HOJE) == 2
    assert calculate_daily_totals([], HOJE)["calorias"] == 0


def test_formatacao_brasileira():
    assert format_number(0) == "0"
    assert format_number(12.0) == "12"
    assert format_number(12.46) == "12,5"
    assert format_date_br("2026-10-21") == "21/10/2026"
    assert format_date_br("") == ""


def test_item_aguardando_analise_nao_mostra_valores():
    item = build_meal_view(refeicao(7, "2026-10-21", 1, calorias=0, descricao="Ovos mexidos", tipo="Café da manhã"))
    assert item == {"id": "7", "tipo": "Café da manhã", "data": "21/10/2026", "descricao": "Ovos mexidos",
                    "analisada": "", "calorias": "", "macros": ""}


def test_item_analisado_mostra_calorias_e_macros():
    item = build_meal_view(refeicao(8, "2026-10-21", 1, analise="ok", calorias=520, proteinas=35.5, carboidratos=60, gorduras=12))
    assert item["analisada"] == "sim"
    assert item["calorias"] == "520 kcal"
    assert item["macros"] == "Proteínas 35,5 g · Carboidratos 60 g · Gorduras 12 g"
