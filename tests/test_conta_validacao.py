from projetofacul.logic.conta_validacao import (
    can_change_email,
    can_change_password,
    is_valid_email,
    is_valid_password,
)


def test_email_valido_e_invalido():
    assert is_valid_email(" Ana@Exemplo.com ")
    assert not is_valid_email("ana@exemplo")
    assert not is_valid_email("")


def test_senha_respeita_minimo_do_xano():
    assert not is_valid_password("1234567")
    assert is_valid_password("12345678")


def test_alterar_email_exige_email_novo_valido_e_senha_atual():
    assert can_change_email("ana@exemplo.com", "nova@exemplo.com", "senha-atual")
    assert not can_change_email("ana@exemplo.com", " ANA@exemplo.com ", "senha-atual")
    assert not can_change_email("ana@exemplo.com", "invalido", "senha-atual")
    assert not can_change_email("ana@exemplo.com", "nova@exemplo.com", "")


def test_alterar_senha_exige_tamanho_minimo_e_senha_atual():
    assert can_change_password("12345678", "senha-atual")
    assert not can_change_password("1234567", "senha-atual")
    assert not can_change_password("12345678", "")
