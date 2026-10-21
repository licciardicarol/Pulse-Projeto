"""Validações de credenciais compartilhadas por cadastro, login e card Conta."""

import re

# mesma regra do input `senha` do signup no Xano (filters=min:8)
TAMANHO_MINIMO_SENHA = 8

PADRAO_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def is_valid_email(email: str) -> bool:
    return bool(PADRAO_EMAIL.fullmatch(normalize_email(email)))


def is_valid_password(senha: str) -> bool:
    return len(senha) >= TAMANHO_MINIMO_SENHA


def can_change_email(email_atual: str, email_novo: str, senha_atual: str) -> bool:
    return (
        is_valid_email(email_novo)
        and normalize_email(email_novo) != normalize_email(email_atual)
        and senha_atual != ""
    )


def can_change_password(nova_senha: str, senha_atual: str) -> bool:
    return is_valid_password(nova_senha) and senha_atual != ""
