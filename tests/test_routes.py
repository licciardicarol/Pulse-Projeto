import json

import reflex as rx

from projetofacul.components.navbar import ITENS_NAVBAR, navbar
from projetofacul.logic.navegacao import ROTAS_PRIVADAS
from projetofacul.pages.perfil_page import perfil_page
from projetofacul.pages.peso_page import peso_page
from projetofacul.pages.refeicoes_page import refeicoes_page
from projetofacul.pages.treinos_page import treinos_page
from projetofacul.pages.placeholder_page import AREAS_EM_CONSTRUCAO
from projetofacul.projetofacul import app, home, redirect_page
from projetofacul.states.sessao_state import SessaoState
from projetofacul.auth_page import pagina_autenticacao
from projetofacul.landing_page import FaqState, PERGUNTAS_FREQUENTES, faq_item
from styles.theme import LANDING_PAGE_CSS


def escapar(texto: str) -> str:
    # o Reflex serializa acentos como sequências \\uXXXX ao converter componentes em texto

    return json.dumps(texto)[1:-1]


def get_routes() -> dict:
    return {rota: pagina.component for rota, pagina in app._unevaluated_pages.items()}


def test_rota_raiz_exibe_home_publica():
    routes = get_routes()

    assert routes["index"] is home
    assert routes["cadastro"] is pagina_autenticacao
    assert routes["login"] is pagina_autenticacao
    assert routes["onboarding"] is redirect_page


def get_on_load_names(rota: str) -> list[str]:
    on_load = app._unevaluated_pages[rota].on_load
    eventos = on_load if isinstance(on_load, list) else [on_load]
    return [evento.fn.__name__ for evento in eventos]


def test_rotas_privadas_exigem_sessao():
    for rota in ROTAS_PRIVADAS:
        # o guarda precisa ser o primeiro evento para nada privado carregar antes dele
        assert get_on_load_names(rota.strip("/"))[0] == SessaoState.ensure_session.fn.__name__


def test_perfil_tem_pagina_propria_e_carrega_dados_apos_guarda():
    assert get_routes()["perfil"] is perfil_page
    assert get_on_load_names("perfil") == ["ensure_session", "load_profile"]
    assert "/perfil" not in AREAS_EM_CONSTRUCAO


def test_placeholders_cobrem_as_demais_rotas_privadas():
    assert set(AREAS_EM_CONSTRUCAO) == set(ROTAS_PRIVADAS) - {"/perfil", "/refeicoes", "/treinos", "/peso"}


def test_refeicoes_tem_pagina_propria_e_carrega_apos_guarda():
    assert get_routes()["refeicoes"] is refeicoes_page
    assert get_on_load_names("refeicoes") == ["ensure_session", "start_page"]
    assert "/refeicoes" not in AREAS_EM_CONSTRUCAO


def test_treinos_tem_pagina_propria_e_carrega_apos_guarda():
    assert get_routes()["treinos"] is treinos_page
    assert get_on_load_names("treinos") == ["ensure_session", "start_page"]
    assert "/treinos" not in AREAS_EM_CONSTRUCAO


def test_peso_tem_pagina_propria_e_carrega_apos_guarda():
    assert get_routes()["peso"] is peso_page
    assert get_on_load_names("peso") == ["ensure_session", "start_page"]
    assert "/peso" not in AREAS_EM_CONSTRUCAO


def test_navbar_tem_itens_sem_social_e_marca_item_ativo():
    assert [rotulo for _, rotulo, _ in ITENS_NAVBAR] == [
        "Início",
        "Treinos",
        "Refeições",
        "Sono",
        "Peso",
        "Relatórios",
        "Perfil",
    ]
    assert {rota for rota, _, _ in ITENS_NAVBAR} == set(ROTAS_PRIVADAS)

    componente = str(navbar("/sono"))
    assert "Social" not in componente
    # o item ativo aparece duas vezes (barra desktop + painel do celular)
    assert componente.count('"aria-current":"page"') == 2
    assert '"aria-expanded"' in componente
    assert escapar("Sair") in componente


def test_onboarding_antigo_redireciona_para_perfil():
    assert get_on_load_names("onboarding") == ["redirect_to_perfil"]


def test_telas_de_acesso_mandam_usuario_logado_para_o_app():
    for rota in ("login", "cadastro"):
        assert "redirect_if_authenticated" in get_on_load_names(rota)


def test_home_possui_novas_secoes_publicas():
    component = home()
    component_text = " ".join(
        str(child)
        for child in component.children
        if hasattr(child, "children")
    )

    assert escapar("Como funciona") in component_text
    assert escapar("Tudo em um só app") in component_text
    assert escapar("Para quem é o Pulse") in component_text
    assert escapar("Perguntas frequentes") in component_text
    assert escapar("Comece hoje o seu histórico") in component_text
    assert "Social (em breve)" not in component_text


def test_home_possui_cabecalho_ordenado():
    component = home()
    component_text = str(component)

    assert component_text.index("Pulse") < component_text.index("Entrar")
    assert component_text.index("Entrar") < component_text.index(escapar("Começar grátis"))
    assert "Social (em breve)" not in component_text


def test_faq_possui_textos_e_estados_acessiveis():
    assert PERGUNTAS_FREQUENTES == (
        ("O Pulse é grátis?", "Sim. Você cria sua conta e usa todos os registros e relatórios sem custo."),
        ("Meus dados são privados?", "Sim. Cada usuário acessa somente os próprios dados: seus registros ficam salvos na sua conta e visíveis só para você."),
        (
            "Preciso pesar a comida para registrar refeições?",
            'Não. Descreva a refeição em texto — por exemplo "2 ovos, pão integral e café" — e a IA estima calorias e macros. Se souber as quantidades exatas, a estimativa fica ainda melhor.',
        ),
        ("Funciona no celular?", "Sim. O app é responsivo e feito para uso rápido no celular, direto do navegador."),
        ("O Pulse substitui orientação profissional?", "Não. As sugestões são geradas por IA como apoio e não substituem médico, nutricionista ou personal trainer."),
    )

    item = faq_item(*PERGUNTAS_FREQUENTES[0], 0)
    button, answer = item.children

    assert button.type._var_value == "button"
    assert button.id == "faq-question-0"
    assert "aria-expanded" in button.custom_attrs
    assert button.custom_attrs["aria-controls"] == "faq-answer-0"
    assert answer.id == "faq-answer-0"
    assert answer.role._var_value == "region"
    assert answer.custom_attrs["aria-labelledby"] == "faq-question-0"
    assert button.event_triggers["on_click"].events[0].handler.fn.__name__ == "toggle_faq"


def test_css_define_breakpoints_e_areas_minimais():
    assert "@media (max-width: 768px)" in LANDING_PAGE_CSS
    assert "@media (min-width: 768px)" not in LANDING_PAGE_CSS
    assert "min-height: 44px" in LANDING_PAGE_CSS
