import re


def normalize_phone_number(phone: str) -> str:
    # Удаляем все нецифровые символы
    digits_only = re.sub(r'\D', '', phone)

    # Если номер начинается с 8, заменяем на 7
    if digits_only.startswith('8'):
        digits_only = '7' + digits_only[1:]

    # Если номер не начинается с 7, добавляем 7 в начало
    if not digits_only.startswith('7'):
        digits_only = '7' + digits_only

    # Форматируем номер как +7XXXXXXXXXX
    return f"+{digits_only}"
