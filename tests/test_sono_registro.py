from datetime import datetime, timezone

import pytest

from projetofacul.logic.sono_registro import (
    build_registro_view,
    build_sono_payload,
    calculate_duration_minutes,
    find_overlap,
    format_conflict_message,
    format_duration,
    format_period,
    from_utc_ms,
    get_form_values,
    parse_local_datetime,
    sort_sono,
    summarize_recent_sleep,
    to_utc_ms,
    validate_sono,
)

BRASILIA = 180
# 21/10/2026 12:00 em Brasília
AGORA = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)


def ms(texto: str) -> int:
    """Horário local de Brasília -> milissegundos UTC, como o Xano guarda."""
    return to_utc_ms(parse_local_datetime(texto), BRASILIA)


def registro(id_, inicio: str, fim: str, qualidade=4, **extra) -> dict:
    return {"id": id_, "inicio_sono": ms(inicio), "fim_sono": ms(fim), "qualidade_sono": qualidade, **extra}


def dados(**campos) -> dict:
    return {"inicio_sono": "2026-10-20T23:00", "fim_sono": "2026-10-21T07:00", "qualidade_sono": 4,
            "observacoes": "", **campos}


@pytest.mark.parametrize(
    ("minutos", "texto"),
    [(480, "8h"), (450, "7h 30min"), (45, "45min"), (61, "1h 1min"), (None, "—"), (0, "—")],
)
def test_formato_da_duracao(minutos, texto):
    assert format_duration(minutos) == texto


def test_duracao_atravessa_a_meia_noite():
    assert calculate_duration_minutes("2026-10-20T23:00", "2026-10-21T07:00") == 480
    assert calculate_duration_minutes("2026-10-20T23:30", "2026-10-21T07:00") == 450
    assert calculate_duration_minutes("2026-10-21T14:00", "2026-10-21T14:45") == 45


@pytest.mark.parametrize(("inicio", "fim"), [("", "2026-10-21T07:00"), ("2026-10-21T07:00", "2026-10-21T07:00"),
                                             ("2026-10-21T08:00", "2026-10-21T07:00"), ("abc", "2026-10-21T07:00")])
def test_duracao_invalida_vira_traco(inicio, fim):
    assert format_duration(calculate_duration_minutes(inicio, fim)) == "—"


def test_intervalo_no_mesmo_dia_mostra_so_as_horas():
    assert format_period(datetime(2026, 10, 21, 14, 0), datetime(2026, 10, 21, 14, 45)) == "14:00 → 14:45"


def test_intervalo_que_passa_da_meia_noite_mostra_os_dois_dias():
    # o dia vira às 00:00 de Brasília
    assert format_period(datetime(2026, 10, 20, 23, 0), datetime(2026, 10, 21, 7, 0)) == "20/10 23:00 → 21/10 07:00"
    assert format_period(datetime(2026, 10, 20, 23, 0), datetime(2026, 10, 21, 0, 0)) == "20/10 23:00 → 21/10 00:00"

def test_conversao_para_utc_e_de_volta():
    # 20/10 23:00 em UTC−3 é 21/10 02:00 UTC
    valor = ms("2026-10-20T23:00")
    assert datetime.fromtimestamp(valor / 1000, tz=timezone.utc) == datetime(2026, 10, 21, 2, 0, tzinfo=timezone.utc)
    assert from_utc_ms(valor, BRASILIA) == datetime(2026, 10, 20, 23, 0)
    assert from_utc_ms(None, BRASILIA) is None


def test_dados_validos_nao_tem_erro():
    assert validate_sono(dados(), AGORA, BRASILIA) == {}


def test_campos_obrigatorios():
    erros = validate_sono(dados(inicio_sono="", fim_sono="", qualidade_sono=0), AGORA, BRASILIA)
    assert erros == {
        "inicio_sono": "Informe o início do sono.",
        "fim_sono": "Informe o fim do sono.",
        "qualidade_sono": "Selecione a qualidade do sono.",
    }


def test_fim_antes_do_inicio():
    erros = validate_sono(dados(fim_sono="2026-10-20T22:00"), AGORA, BRASILIA)
    assert erros["fim_sono"] == "O fim do sono precisa ser depois do início."


def test_fim_no_futuro():
    erros = validate_sono(dados(inicio_sono="2026-10-21T11:00", fim_sono="2026-10-21T13:00"), AGORA, BRASILIA)
    assert erros["fim_sono"] == "O fim do sono não pode estar no futuro."


def test_fim_igual_a_agora_e_aceito():
    assert validate_sono(dados(inicio_sono="2026-10-21T11:00", fim_sono="2026-10-21T12:00"), AGORA, BRASILIA) == {}


def test_duracao_minima_e_maxima():
    curta = validate_sono(dados(inicio_sono="2026-10-21T06:50", fim_sono="2026-10-21T07:00"), AGORA, BRASILIA)
    longa = validate_sono(dados(inicio_sono="2026-10-20T06:00", fim_sono="2026-10-21T07:00"), AGORA, BRASILIA)
    assert curta["fim_sono"] == "O registro precisa ter pelo menos 15 minutos."
    assert longa["fim_sono"] == "O registro pode ter no máximo 24 horas."
    assert validate_sono(dados(inicio_sono="2026-10-21T06:45"), AGORA, BRASILIA) == {}
    assert validate_sono(dados(inicio_sono="2026-10-20T07:00"), AGORA, BRASILIA) == {}


@pytest.mark.parametrize("qualidade", [0, 6, 7, "4", None])
def test_qualidade_fora_de_1_a_5(qualidade):
    assert "qualidade_sono" in validate_sono(dados(qualidade_sono=qualidade), AGORA, BRASILIA)


def test_observacoes_ate_500_caracteres():
    assert validate_sono(dados(observacoes="a" * 500), AGORA, BRASILIA) == {}
    assert "observacoes" in validate_sono(dados(observacoes="a" * 501), AGORA, BRASILIA)


def test_sobreposicao_detecta_conflito():
    existente = registro(1, "2026-10-20T23:00", "2026-10-21T07:00")
    conflito = find_overlap(ms("2026-10-21T06:00"), ms("2026-10-21T08:00"), [existente])
    assert conflito is existente
    assert format_conflict_message(conflito, BRASILIA) == (
        "Já existe um registro de sono nesse período (20/10 23:00 → 21/10 07:00). Ajuste os horários."
    )


def test_periodos_encostados_nao_se_sobrepoem():
    existente = registro(1, "2026-10-20T23:00", "2026-10-21T07:00")
    assert find_overlap(ms("2026-10-21T07:00"), ms("2026-10-21T08:00"), [existente]) is None
    assert find_overlap(ms("2026-10-20T21:00"), ms("2026-10-20T23:00"), [existente]) is None


def test_sobreposicao_ignora_o_proprio_registro_em_edicao():
    existente = registro(1, "2026-10-20T23:00", "2026-10-21T07:00")
    assert find_overlap(ms("2026-10-20T23:00"), ms("2026-10-21T07:00"), [existente], ignorar_id="1") is None


def test_payload_em_utc_sem_dono_nem_duracao():
    payload = build_sono_payload(dados(observacoes="  acordei 2x  "), BRASILIA)
    assert payload == {
        "inicio_sono": ms("2026-10-20T23:00"),
        "fim_sono": ms("2026-10-21T07:00"),
        "qualidade_sono": 4,
        "observacoes": "acordei 2x",
    }
    assert build_sono_payload(dados(observacoes="   "), BRASILIA)["observacoes"] is None


def test_ordena_do_mais_recente_para_o_mais_antigo():
    lista = [registro(18, "2026-10-17T23:00", "2026-10-18T07:00"),
             registro(20, "2026-10-19T23:00", "2026-10-20T07:00"),
             registro(19, "2026-10-18T23:00", "2026-10-19T07:00")]
    assert [r["id"] for r in sort_sono(lista)] == [20, 19, 18]


def test_item_da_lista_no_fuso_do_usuario():
    item = build_registro_view(registro(5, "2026-10-20T23:30", "2026-10-21T07:00", 5, observacoes="Café tarde"), BRASILIA)
    assert item == {
        "id": "5",
        "data": "21/10/2026",
        "intervalo": "20/10 23:30 → 21/10 07:00",
        "duracao": "7h 30min",
        "qualidade": "5",
        "rotulo_qualidade": "Muito bom",
        "descricao_qualidade": "Qualidade 5 de 5: Muito bom",
        "observacoes": "Café tarde",
    }


def test_item_usa_duracao_do_servidor_quando_existe():
    item = build_registro_view(registro(5, "2026-10-20T23:00", "2026-10-21T07:00", duracao_minutos=470), BRASILIA)
    assert item["duracao"] == "7h 50min"


def test_valores_para_editar():
    valores = get_form_values(registro(5, "2026-10-20T23:00", "2026-10-21T07:00", 2, observacoes="x"), BRASILIA)
    assert valores == {"inicio_sono": "2026-10-20T23:00", "fim_sono": "2026-10-21T07:00", "qualidade_sono": 2, "observacoes": "x"}


def test_resumo_das_ultimas_7_noites():
    lista = [registro(dia, f"2026-10-{dia - 1:02d}T23:00", f"2026-10-{dia:02d}T07:00", qualidade=3 if dia > 13 else 1)
             for dia in range(11, 21)]
    resumo = summarize_recent_sleep(lista, 7, BRASILIA)
    assert resumo["quantidade"] == 7
    assert resumo["duracao_media_minutos"] == 480
    assert resumo["qualidade_media"] == 3
    assert resumo["noites"][0] == {"data": "2026-10-20", "duracao_minutos": 480, "qualidade": 3}
    assert resumo["noites"][-1]["data"] == "2026-10-14"


def test_resumo_sem_registros():
    assert summarize_recent_sleep([]) == {
        "quantidade": 0, "duracao_media_minutos": None, "qualidade_media": None, "noites": [],
    }
