
"""
Лабораторна робота № 5.
Модуль базового очищення та нормалізації тексту.
Освітній компонент: Програмування на Python.
"""

import re


def sanitize_log_line(raw_line: str) -> str:
    """
    Виконує базове очищення та нормалізацію вхідного рядка журналу:
    видаляє кінцеві пробіли та символи переходу рядка.
    """
    cleaned_line = raw_line.strip()
    return cleaned_line


def normalize_log_line(raw_line: str) -> str:
    """
    Нормалізує пробіли між полями текстового журналу.
    """
    cleaned_line = sanitize_log_line(raw_line)

    # Видалення зайвих пробілів біля роздільника
    normalized_line = re.sub(r"\s*\|\s*", " | ", cleaned_line)

    return normalized_line
