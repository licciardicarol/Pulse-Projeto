import reflex as rx

from projetofacul.projetofacul import app, cadastro, home, login


def test_rota_raiz_exibe_home_publica():
    routes = {page.route: page.component for page in app.pages}

    assert routes["/"] is home
    assert routes["/cadastro"] is cadastro
    assert routes["/login"] is login


def test_home_possui_novas_secoes_publicas():
    component = home()
    component_text = " ".join(
        str(child)
        for child in component.children
        if hasattr(child, "children")
    )

    assert "Como funciona" in component_text
    assert "Tudo em um só app" in component_text
    assert "Para quem é o Pulse" in component_text
    assert "Perguntas frequentes" in component_text
    assert "Comece hoje o seu histórico" in component_text
    assert "Social (em breve)" not in component_text


def test_home_possui_cabecalho_ordenado():
    component = home()
    component_text = str(component)

    assert component_text.index("Pulse") < component_text.index("Entrar")
    assert component_text.index("Entrar") < component_text.index("Começar grátis")
    assert "Social (em breve)" not in component_text


def test_faq_possui_textos_e_estados_acessiveis():
    component = home()
    component_text = str(component)

    assert "O Pulse é grátis?" in component_text
    assert "Sim. Você cria sua conta e usa todos os registros e relatórios sem custo." in component_text
    assert "Meus dados são privados?" in component_text
    assert "Sim. Cada usuário acessa somente os próprios dados: seus registros ficam salvos na sua conta e visíveis só para você." in component_text
    assert "Preciso pesar a comida para registrar refeições?" in component_text
    assert 'Não. Descreva a refeição em texto — por exemplo "2 ovos, pão integral e café" — e a IA estima calorias e macros. Se souber as quantidades exatas, a estimativa fica ainda melhor.' in component_text
    assert "Funciona no celular?" in component_text
    assert "Sim. O app é responsivo e feito para uso rápido no celular, direto do navegador." in component_text
    assert "O Pulse substitui orientação profissional?" in component_text
    assert "Não. As sugestões são geradas por IA como apoio e não substituem médico, nutricionista ou personal trainer." in component_text
    assert 'aria-expanded' in component_text
    assert 'aria-controls' in component_text
    assert 'type_="single"' in component_text
    assert 'collapsible=True' in component_text


def test_css_define_breakpoints_e_areas_minimais():
    component = home()
    component_text = str(component)

    assert "@media (max-width: 768px)" in component_text
    assert "@media (min-width: 768px)" in component_text
    assert "min-height: 44px" in component_text
