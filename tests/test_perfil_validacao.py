import re
from datetime import date
from pathlib import Path

import pytest

from projetofacul.logic.perfil_opcoes import (
    OPCOES_CONDICIONAMENTO,
    OPCOES_HORARIO,
    OPCOES_MODALIDADES,
    OPCOES_OBJETIVO,
    OPCOES_SEXO,
    VALORES_BIOTIPO,
)
from projetofacul.logic.perfil_validacao import (
    build_form_from_perfil,
    build_perfil_payload,
    validate_perfil,
)

HOJE = date(2026, 10, 16)
RAIZ = Path(__file__).resolve().parent.parent
ARQUIVOS_XANO = (
    RAIZ / "xano" / "table" / "perfil.xs",
    RAIZ / "xano" / "api" / "lunas_workspace" / "perfil" / "me_PATCH.xs",
)


def dados_validos(**alteracoes):
    dados = {
        "nome": "Ana Souza",
        "data_de_nascimento": "1995-04-20",
        "sexo": "Feminino",
        "altura_cm": "165",
        "tipo_fisico": "Mesomorfo",
        "nivel_fisico": "Intermediário",
        "horario_fav_de_treino": "Manhã",
        "meta_semanal": "4",
        "objetivo": "Hipertrofia (ganho de massa muscular)",
        "modalidade_fav1": ["Musculação", "Yoga"],
    }
    dados.update(alteracoes)
    return dados


def test_dados_validos_nao_geram_erros():
    assert validate_perfil(dados_validos(), HOJE) == {}


@pytest.mark.parametrize(
    "campo",
    [
        "nome",
        "data_de_nascimento",
        "sexo",
        "altura_cm",
        "tipo_fisico",
        "nivel_fisico",
        "horario_fav_de_treino",
        "meta_semanal",
        "objetivo",
    ],
)
def test_cada_campo_obrigatorio_vazio_gera_erro_so_nele(campo):
    erros = validate_perfil(dados_validos(**{campo: ""}), HOJE)

    assert list(erros) == [campo]


def test_formulario_todo_vazio_aponta_todos_os_campos():
    erros = validate_perfil({}, HOJE)

    assert set(erros) == {
        "nome",
        "data_de_nascimento",
        "sexo",
        "altura_cm",
        "tipo_fisico",
        "nivel_fisico",
        "horario_fav_de_treino",
        "meta_semanal",
        "objetivo",
        "modalidade_fav1",
    }


def test_nome_so_com_espacos_ou_longo_demais():
    assert "nome" in validate_perfil(dados_validos(nome="   "), HOJE)
    assert "nome" in validate_perfil(dados_validos(nome="a" * 51), HOJE)
    assert validate_perfil(dados_validos(nome="a" * 50), HOJE) == {}


@pytest.mark.parametrize("nascimento", ["2026-10-17", "2026-10-16", "1899-12-31", "20/04/1995", "1995-02-30"])
def test_data_de_nascimento_invalida(nascimento):
    assert "data_de_nascimento" in validate_perfil(dados_validos(data_de_nascimento=nascimento), HOJE)


def test_data_de_nascimento_nos_limites():
    assert validate_perfil(dados_validos(data_de_nascimento="1900-01-01"), HOJE) == {}
    assert validate_perfil(dados_validos(data_de_nascimento="2026-10-15"), HOJE) == {}


@pytest.mark.parametrize("altura", ["0", "-170", "abc", "99.9", "250.1", "nan", "inf"])
def test_altura_implausivel(altura):
    assert "altura_cm" in validate_perfil(dados_validos(altura_cm=altura), HOJE)


@pytest.mark.parametrize("altura", ["100", "250", "175,5", " 180 "])
def test_altura_aceita_faixa_e_virgula(altura):
    assert validate_perfil(dados_validos(altura_cm=altura), HOJE) == {}


@pytest.mark.parametrize("meta", ["0", "15", "3.5", "abc", "-2"])
def test_meta_semanal_fora_da_faixa(meta):
    assert "meta_semanal" in validate_perfil(dados_validos(meta_semanal=meta), HOJE)


@pytest.mark.parametrize("meta", ["1", "14", "7"])
def test_meta_semanal_valida(meta):
    assert validate_perfil(dados_validos(meta_semanal=meta), HOJE) == {}


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("sexo", "Selecione"),
        ("tipo_fisico", "Mesoformo"),
        ("nivel_fisico", "Profissional"),
        ("horario_fav_de_treino", "Almoço"),
        # valor curto que chegou a ser proposto, mas não existe no Xano
        ("objetivo", "Ganhar massa"),
    ],
)
def test_opcao_fora_da_lista_e_recusada(campo, valor):
    assert campo in validate_perfil(dados_validos(**{campo: valor}), HOJE)


def test_modalidades_exigem_ao_menos_uma_opcao_valida():
    assert "modalidade_fav1" in validate_perfil(dados_validos(modalidade_fav1=[]), HOJE)
    assert "modalidade_fav1" in validate_perfil(dados_validos(modalidade_fav1=["Corrida"]), HOJE)
    assert validate_perfil(dados_validos(modalidade_fav1=["Pilates"]), HOJE) == {}


def test_payload_converte_tipos_e_preserva_medidas():
    payload = build_perfil_payload(
        dados_validos(
            nome="  Ana Souza ",
            altura_cm="165,5",
            modalidade_fav1=["Yoga", "Musculação", "Yoga"],
        ),
        medidas=True,
    )

    assert payload == {
        "nome": "Ana Souza",
        "data_de_nascimento": "1995-04-20",
        "sexo": "Feminino",
        "altura_cm": 165.5,
        "tipo_fisico": "Mesomorfo",
        "nivel_fisico": "Intermediário",
        "modalidade_fav1": ["Musculação", "Yoga"],
        "horario_fav_de_treino": "Manhã",
        "meta_semanal": 4,
        "objetivo": "Hipertrofia (ganho de massa muscular)",
        "medidas": True,
    }
    assert "user_id" not in payload
    assert "onboarding_concluido" not in payload


def test_formulario_de_perfil_recem_criado_so_tem_nome():
    formulario = build_form_from_perfil(
        {"nome": "Ana Souza", "onboarding_concluido": False, "medidas": False, "modalidade_fav1": None}
    )

    assert formulario == {
        "nome": "Ana Souza",
        "data_de_nascimento": "",
        "altura_cm": "",
        "meta_semanal": "",
        "modalidade_fav1": [],
        "sexo": "",
        "tipo_fisico": "",
        "nivel_fisico": "",
        "horario_fav_de_treino": "",
        "objetivo": "",
    }


def test_formulario_de_perfil_salvo_e_descarte_de_valores_antigos():
    formulario = build_form_from_perfil(
        {
            "nome": "Ana Souza",
            "data_de_nascimento": "1995-04-20",
            "sexo": "Feminino",
            "altura_cm": 165.0,
            "tipo_fisico": "Endomorfo",
            "nivel_fisico": "Atleta",
            "horario_fav_de_treino": "Noite",
            "meta_semanal": 5,
            "objetivo": "Ganhar massa",
            "modalidade_fav1": ["Yoga", "Corrida", "Pilates"],
        }
    )

    assert formulario["altura_cm"] == "165"
    assert formulario["meta_semanal"] == "5"
    assert formulario["nivel_fisico"] == "Atleta"
    assert formulario["objetivo"] == ""
    assert formulario["modalidade_fav1"] == ["Yoga", "Pilates"]


def read_xano_enum(conteudo: str, campo: str) -> list[str]:
    padrao = r"enum(?:\[\])?\??\s+" + campo + r"\??\s*\{\s*values\s*=\s*\[(.*?)\]"
    encontrado = re.search(padrao, conteudo, re.DOTALL)
    assert encontrado, f"enum {campo} não encontrado"
    return re.findall(r'"([^"]*)"', encontrado.group(1))


@pytest.mark.parametrize("arquivo", ARQUIVOS_XANO, ids=lambda caminho: caminho.name)
def test_opcoes_iguais_aos_enums_do_xano(arquivo):
    conteudo = arquivo.read_text(encoding="utf-8")
    esperado = {
        "sexo": OPCOES_SEXO,
        "tipo_fisico": VALORES_BIOTIPO,
        "nivel_fisico": OPCOES_CONDICIONAMENTO,
        "horario_fav_de_treino": OPCOES_HORARIO,
        "objetivo": OPCOES_OBJETIVO,
        "modalidade_fav1": OPCOES_MODALIDADES,
    }

    for campo, opcoes in esperado.items():
        assert set(read_xano_enum(conteudo, campo)) == set(opcoes), campo
