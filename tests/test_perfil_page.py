import json
import re

from projetofacul.logic.perfil_opcoes import (
    OPCOES_BIOTIPO,
    OPCOES_CONDICIONAMENTO,
    OPCOES_HORARIO,
    OPCOES_MODALIDADES,
    OPCOES_OBJETIVO,
    OPCOES_SEXO,
)
from projetofacul.pages.perfil_page import (
    PERFIL_PAGE_CSS,
    modalidade_chip,
    perfil_page,
    select_input,
)


def escapar(texto: str) -> str:
    # o Reflex serializa acentos como sequências \\uXXXX ao converter componentes em texto
    return json.dumps(texto)[1:-1]


PAGINA = str(perfil_page())


def get_options(componente: str) -> list[str]:
    return re.findall(r'jsx\("option",\{[^}]*\},"([^"]*)"\)', componente)


def test_tres_cards_na_ordem_e_sem_cards_adiados():
    titulos = ["Dados pessoais", "Biotipo corporal", escapar("Preferências de treino"), "Salvar perfil"]
    posicoes = [PAGINA.index(titulo) for titulo in titulos]

    assert posicoes == sorted(posicoes)
    assert PAGINA.count('className:"perfil-card"') == 3
    for ausente in ("Minhas metas", escapar("Preferências de registro"), "Alterar", "Social"):
        assert ausente not in PAGINA


def test_cabecalho_e_faixa_de_onboarding():
    assert escapar(
        "Suas informações pessoais e preferências de treino, usadas para personalizar "
        "as recomendações e o cálculo de calorias."
    ) in PAGINA
    assert escapar("Complete seu perfil para personalizar suas recomendações") in PAGINA
    assert "onboarding_concluido" in PAGINA


def test_campos_tem_rotulo_associado_e_autocomplete():
    for input_id in (
        "perfil-nome",
        "perfil-nascimento",
        "perfil-sexo",
        "perfil-altura",
        "perfil-condicionamento",
        "perfil-horario",
        "perfil-meta",
        "perfil-objetivo",
    ):
        assert f'htmlFor:"{input_id}"' in PAGINA
        assert f'"aria-describedby":"{input_id}-erro"' in PAGINA
        assert f'id:"{input_id}-erro"' in PAGINA

    for autocomplete in ('autoComplete:"name"', 'autoComplete:"bday"', 'autoComplete:"sex"'):
        assert autocomplete in PAGINA


def test_meta_semanal_e_altura_sao_numericas():
    assert PAGINA.count('type:"number"') == 2
    assert 'type:"date"' in PAGINA


def test_selects_tem_opcoes_exatas_com_placeholder():
    for campo, opcoes in (
        ("sexo", OPCOES_SEXO),
        ("nivel_fisico", OPCOES_CONDICIONAMENTO),
        ("horario_fav_de_treino", OPCOES_HORARIO),
        ("objetivo", OPCOES_OBJETIVO),
    ):
        componente = str(select_input(campo, f"teste-{campo}", opcoes))
        assert get_options(componente) == ["Selecione", *[escapar(opcao) for opcao in opcoes]]
        assert 'disabled:true,value:""' in componente or 'value:"",disabled:true' in componente


def test_condicionamento_tem_cinco_niveis():
    assert OPCOES_CONDICIONAMENTO == ("Sedentário", "Iniciante", "Intermediário", "Avançado", "Atleta")
    assert OPCOES_OBJETIVO[0] == "Hipertrofia (ganho de massa muscular)" and len(OPCOES_OBJETIVO) == 4
    assert OPCOES_HORARIO == ("Manhã", "Tarde", "Noite", "Madrugada")


def test_biotipo_e_grupo_de_radio_de_escolha_unica():
    assert '"role":"radiogroup"' in PAGINA or 'role:"radiogroup"' in PAGINA
    assert PAGINA.count('type:"radio"') == 3
    assert PAGINA.count('name:"tipo_fisico"') == 3
    for valor, descricao in OPCOES_BIOTIPO:
        assert escapar(descricao) in PAGINA
        # cada rádio fica marcado só quando tipo_fisico é igual ao seu valor
        assert f'=== "{valor}"' in PAGINA


def test_oito_chips_de_modalidade_com_aria_pressed():
    assert len(OPCOES_MODALIDADES) == 8
    assert PAGINA.count('className:(reflex___state') >= 8
    for modalidade in OPCOES_MODALIDADES:
        chip = str(modalidade_chip(modalidade))
        assert '"aria-pressed"' in chip
        assert 'type:"button"' in chip
        assert escapar(modalidade) in PAGINA


def test_erros_e_botao_acessiveis():
    assert '"aria-live":"polite"' in PAGINA
    assert '"aria-busy"' in PAGINA
    assert "salvando" in PAGINA


def test_css_espaco_entre_cards_responsivo_e_movimento_reduzido():
    assert ".perfil-cards { display: grid; gap: 32px; }" in PERFIL_PAGE_CSS
    assert "@media (max-width: 768px)" in PERFIL_PAGE_CSS
    assert "min-height: 44px" in PERFIL_PAGE_CSS
    assert "prefers-reduced-motion" in PERFIL_PAGE_CSS
    assert "__" not in PERFIL_PAGE_CSS
