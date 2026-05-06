from string import ascii_letters, digits

from email_validator import validate_email, EmailNotValidError

PUNCTUATION = "!@#$%^&*"


def check_email(email: str) -> bool:
    try:
        validate_email(email)

        return True
    except EmailNotValidError:
        return False


def check_password(password: str):
    if not password:
        return "Введіть пароль"

    elif len(password) < 6:
        return "Мінімальна довжина паролю - 6 символів"

    ltr = dgt = pnc = 0
    for letter in password:
        if letter in ascii_letters:
            ltr += 1
        elif letter in digits:
            dgt += 1
        elif letter in PUNCTUATION:
            pnc += 1

    if not all([ltr, dgt, pnc]):
        return 'Пароль повинен містити букви (a-Z), \nспецсимволи ("!@#$%^&*") та цифри (0-9)'
