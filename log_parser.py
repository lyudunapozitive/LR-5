
"""
Лабораторна робота № 5.
Синтаксичний розбір журналу Git Audit регулярними виразами
та формування табличних звітів через f-strings.
Варіант 20.
"""

import re
import sys
import time
from pathlib import Path


# Регулярний вираз з іменованими групами для розбору Git Audit
# Формат: Commit_Hash | Author_Name | Email | Timestamp_ISO | Message
LOG_PATTERN = re.compile(
    r"^(?P<Commit_Hash>[0-9a-fA-F]{40})\s*\|\s*"
    r"(?P<Author_Name>[^|]+?)\s*\|\s*"
    r"(?P<Email>[^|]+?)\s*\|\s*"
    r"(?P<Timestamp_ISO>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?)\s*\|\s*"
    r"(?P<Message>.+?)$"
)

# Перевірка електронної адреси
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

# Перевірка стандарту Conventional Commits
COMMIT_PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([a-zA-Z0-9._/-]+\))?(!)?: .+"
)


def sanitize_log_line(raw_line: str) -> str:
    """
    Виконує базове очищення та нормалізацію вхідного рядка журналу:
    видаляє кінцеві пробіли та символи переходу рядка.
    """
    cleaned_line = raw_line.strip()
    return cleaned_line


def validate_extracted_data(record: dict) -> bool:
    """
    Здійснює перевірку параметрів запису Git Audit:
    перевіряє email та відповідність Conventional Commits.
    """
    email = record["Email"]
    message = record["Message"]

    email_valid = EMAIL_PATTERN.fullmatch(email) is not None
    commit_valid = COMMIT_PATTERN.fullmatch(message) is not None

    record["email_valid"] = email_valid
    record["commit_valid"] = commit_valid

    return email_valid and commit_valid


def parse_telemetry_file(file_path: Path) -> list[dict]:
    """
    Зчитує лог-файл, виконує построкову фільтрацію та вилучає
    структуровані словники за допомогою скомпільованого регулярного виразу.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Вхідний файл журналу '{file_path}' не знайдено.")

    parsed_records = []

    with open(file_path, mode="r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            normalized = sanitize_log_line(line)

            if not normalized or normalized.startswith("#"):
                continue

            match = LOG_PATTERN.search(normalized)

            if match:
                record = match.groupdict()

                record["line_num"] = line_num
                validate_extracted_data(record)
                parsed_records.append(record)
            else:
                print(f"Помилка парсингу: Рядок {line_num} не відповідає формату Git Audit.")

    return parsed_records


def generate_ascii_report(records: list[dict]) -> None:
    """
    Генерує інженерний звіт із фіксованою шириною колонок,
    вирівнюванням та підрахунком статистики за допомогою f-strings.
    """
    header_sep = "=" * 100
    row_sep = "-" * 100

    print("\n" + header_sep)
    print(f"{'ЗВІТ АНАЛІЗУ ЖУРНАЛУ GIT AUDIT':^100}")
    print(header_sep)

    print(
        f"| {'Хеш коміту':<12} | {'Автор':<20} | "
        f"{'Email':<30} | {'Перевірка':<10} |"
    )
    print(row_sep)

    valid_count = 0
    invalid_count = 0

    for rec in records:
        is_valid = rec["email_valid"] and rec["commit_valid"]
        status = "OK" if is_valid else "ERROR"

        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1

        print(
            f"| {rec['Commit_Hash'][:12]:<12} | "
            f"{rec['Author_Name']:<20} | "
            f"{rec['Email']:<30} | "
            f"{status:<10} |"
        )

        print(f"  Дата: {rec['Timestamp_ISO']}")
        print(f"  Повідомлення: {rec['Message']}")
        print(f"  Email: {'OK' if rec['email_valid'] else 'ERROR'}")
        print(f"  Conventional Commits: {'OK' if rec['commit_valid'] else 'ERROR'}")
        print(row_sep)

    print(header_sep)
    print(f"{'ПІДСУМКОВА СТАТИСТИКА GIT AUDIT':^100}")
    print(row_sep)
    print(f"  Всього проаналізовано комітів: {len(records):>5d}")
    print(f"  Коректних комітів:           {valid_count:>5d}")
    print(f"  Некоректних комітів:         {invalid_count:>5d}")
    print(header_sep + "\n")


def main() -> None:
    """Головна точка входу модуля обробки журналу Git Audit."""
    log_file_path = Path("input_logs.txt")

    t_start = time.perf_counter()
    records = parse_telemetry_file(log_file_path)
    generate_ascii_report(records)
    t_elapsed = time.perf_counter() - t_start

    print(f"Час виконання повного циклу аналізу тексту: {t_elapsed * 1000:.3f} мс\n")


if __name__ == "__main__":
    main()
