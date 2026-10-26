from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from projetofacul.logic.peso import (
    FUSO_BRASILIA,
    build_registro_payload,
    build_weight_view,
    calculate_change_since_first,
    format_change,
    format_weight,
    from_milliseconds,
    get_current_weight,
    parse_weight,
    sort_registros,
    validate_registro_peso,
)

# 23/10/2026 17:38 em Brasília = 20:38 UTC
MS_1738 = 1792787880000
AGORA = datetime(2026, 10, 23, 18, 0, tzinfo=FUSO_BRASILIA)


def dados(**campos):
    return {"data": "2026-10-23", "horario": "17:38", "peso": "70,0", **campos}


@pytest.mark.parametrize(("texto", "esperado"), [("70,5", Decimal("70.5")), ("70.25", Decimal("70.25")), (" 82 ", Decimal("82"))])
def test_peso_aceita_virgula_ou_ponto(texto, esperado):
    assert parse_weight(texto) == esperado


@pytest.mark.parametrize("texto", ["abc", "70,123", "-70", "70,", "1e2", "", "7 0"])
def test_peso_com_formato_invalido(texto):
    assert parse_weight(texto) is None


@pytest.mark.parametrize("peso", ["20", "400", "20,00", "70,25"])
def test_peso_dentro_da_faixa_e_valido(peso):
    assert validate_registro_peso(dados(peso=peso), AGORA) == {}


@pytest.mark.parametrize("peso", ["0", "19,99", "400,01", "70,123", "abc", ""])
def test_peso_invalido_mostra_erro_no_campo(peso):
    assert "peso" in validate_registro_peso(dados(peso=peso), AGORA)


def test_data_e_horario_obrigatorios():
    erros = validate_registro_peso(dados(data="", horario=""), AGORA)
    assert set(erros) == {"data", "horario"}


def test_data_futura_recusada():
    erros = validate_registro_peso(dados(data="2026-10-24", horario="08:00"), AGORA)
    assert "data" in erros and "horario" not in erros


def test_horario_futuro_no_mesmo_dia_recusado():
    erros = validate_registro_peso(dados(horario="18:01"), AGORA)
    assert erros == {"horario": "O horário não pode estar no futuro."}


def test_agora_em_utc_e_comparado_no_horario_de_brasilia():
    # 23/10 às 23h30 em Brasília já é 24/10 em UTC: hoje continua sendo 23/10
    agora_utc = datetime(2026, 10, 24, 2, 30, tzinfo=timezone.utc)
    assert validate_registro_peso(dados(horario="23:00"), agora_utc) == {}
    assert "data" in validate_registro_peso(dados(data="2026-10-24", horario="00:10"), agora_utc)


def test_payload_converte_horario_de_brasilia_para_ms_utc():
    assert build_registro_payload(dados(peso="70,5")) == {"peso": 70.5, "data_horario": MS_1738}


def test_horario_volta_sem_deslocamento():
    momento = from_milliseconds(MS_1738)
    assert (momento.day, momento.hour, momento.minute) == (23, 17, 38)
    assert build_weight_view({"id": 1, "peso": 70, "data_horario": MS_1738}) == {
        "id": "1",
        "peso": "70,0 kg",
        "data_hora": "23/10/2026 · 17:38",
    }


def test_registro_sem_horario_mostra_traco():
    assert build_weight_view({"id": 2, "peso": 70.5, "data_horario": None})["data_hora"] == "—"


def registro(id_, peso, dia, criado):
    momento = datetime(2026, 10, dia, 8, 0, tzinfo=FUSO_BRASILIA)
    return {"id": id_, "peso": peso, "data_horario": int(momento.timestamp() * 1000), "created_at": criado}


def test_ordena_pela_data_da_pesagem_e_nao_pela_criacao():
    registros = [registro(1, 70.0, 23, 1), registro(2, 69.0, 20, 2)]
    assert [item["id"] for item in sort_registros(registros)] == [1, 2]


def test_peso_atual_e_o_da_pesagem_mais_recente():
    # o de 69 kg foi criado depois, mas a pesagem é de antes
    registros = [registro(1, 70.0, 23, 1), registro(2, 69.0, 20, 2)]
    assert get_current_weight(registros) == 70.0
    assert format_change(calculate_change_since_first(registros)) == "+1,0 kg"


def test_variacao_negativa_e_zero():
    assert format_change(calculate_change_since_first([registro(1, 71.2, 20, 1), registro(2, 70.0, 23, 2)])) == "-1,2 kg"
    assert format_change(calculate_change_since_first([registro(1, 70.0, 20, 1), registro(2, 70.0, 23, 2)])) == "0,0 kg"


def test_um_registro_ou_nenhum_mostra_traco():
    assert format_change(calculate_change_since_first([registro(1, 70.0, 23, 1)])) == "—"
    assert format_weight(get_current_weight([])) == "—"


@pytest.mark.parametrize(("valor", "texto"), [(70, "70,0 kg"), (70.5, "70,5 kg"), (70.25, "70,25 kg"), (70.05, "70,05 kg")])
def test_formato_brasileiro_do_peso(valor, texto):
    assert format_weight(valor) == texto


def test_nenhuma_funcao_estima_meta():
    import projetofacul.logic.peso as modulo

    assert not [nome for nome in dir(modulo) if "meta" in nome.lower() or "goal" in nome.lower()]
