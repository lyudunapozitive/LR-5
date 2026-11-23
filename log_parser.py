"""
Лабораторна робота № 5.
Синтаксичний розбір журналів мережевого комутатора регулярними виразами
та формування табличних інженерних звітів через f-strings.
Освітній компонент: Програмування на Python.
"""

import re
import sys
import time
from pathlib import Path


# Регулярний вираз із іменованими групами для розбору телеметрії порту
# Формат: YYYY-MM-DD HH:MM:SS | Switch | Port: ... | MAC: ... | VLAN: ... | Status: ... | Speed: ... | Duplex: ...
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s*\|\s*"
    r"(?P<switch_id>[A-Za-z0-9_\-]+)\s*\|\s*"
    r"Port:\s*(?P<port_name>[A-Za-z0-9/]+)\s*\|\s*"
    r"MAC:\s*(?P<mac_address>[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})\s*\|\s*"
    r"VLAN:\s*(?P<vlan_id>\d+)\s*\|\s*"
    r"Status:\s*(?P<link_status>UP|DOWN)\s*\|\s*"
    r"Speed:\s*(?P<speed_mbps>\d+)Mbps\s*\|\s*"
    r"Duplex:\s*(?P<duplex_mode>FULL|HALF|AUTO)$"
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
    Здійснює семантичну валідацію вилучених параметрів кадру:
    перевіряє коректність діапазону VLAN (1..4094) та допустимі значення швидкості.
    """
    vlan = int(record["vlan_id"])
    speed = int(record["speed_mbps"])

    if not (1 <= vlan <= 4094):
        return False
    if speed not in (0, 10, 100, 1000, 10000, 40000, 100000):
        return False
    return True


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
                continue  # Пропуск порожніх рядків та коментарів

            match = LOG_PATTERN.search(normalized)
            if match:
                record = match.groupdict()
                if validate_extracted_data(record):
                    # Приведення числових полів до відповідних скалярних типів
                    record["vlan_id"] = int(record["vlan_id"])
                    record["speed_mbps"] = int(record["speed_mbps"])
                    record["line_num"] = line_num
                    parsed_records.append(record)
                else:
                    print(f"Попередження: Рядок {line_num} містить невалідні параметри.")
            else:
                print(f"Помилка парсингу: Рядок {line_num} не відповідає формату: '{normalized}'")

    return parsed_records


def generate_ascii_report(records: list[dict]) -> None:
    """
    Генерує високоякісний інженерний звіт з фіксованою шириною колонок,
    вирівнюванням та агрегацією пропускної здатності за допомогою f-strings.
    """
    header_sep = "=" * 98
    row_sep = "-" * 98

    print("\n" + header_sep)
    print(f"{'ЗВІТ СТАНУ ІНТЕРФЕЙСІВ МЕРЕЖЕВОГО КОМУТАТОРА':^98}")
    print(header_sep)
    print(
        f"| {'Часова мітка':^19} | {'Інтерфейс':^18} | {'MAC-адреса':^17} | "
        f"{'VLAN':^5} | {'Статус':^6} | {'Швидкість':^10} | {'Дуплекс':^6} |"
    )
    print(row_sep)

    total_bandwidth_mbps = 0
    active_ports_count = 0

    for rec in records:
        status_marker = rec["link_status"]
        speed_str = f"{rec['speed_mbps']} Mbps" if rec["speed_mbps"] > 0 else "N/A"

        if rec["link_status"] == "UP":
            active_ports_count += 1
            total_bandwidth_mbps += rec["speed_mbps"]

        # Форматований рядок із роздільниками та точним вирівнюванням
        print(
            f"| {rec['timestamp']:<19} | {rec['port_name']:<18} | {rec['mac_address']:<17} | "
            f"{rec['vlan_id']:>5d} | {status_marker:^6} | {speed_str:>10} | {rec['duplex_mode']:^6} |"
        )

    print(header_sep)
    print(f"{'ПІДСУМКОВА СТАТИСТИКА КОМУТАТОРА':^98}")
    print(row_sep)
    print(f"  Всього проаналізовано інтерфейсів: {len(records):>5d}")
    print(f"  Активних інтерфейсів (Link UP):   {active_ports_count:>5d}")
    print(f"  Сумарна комутаційна ємність:      {total_bandwidth_mbps / 1000:>8.2f} Gbps ({total_bandwidth_mbps:,} Mbps)")
    print(header_sep + "\n")


def main() -> None:
    """Головна точка входу модуля обробки логів."""
    log_file_path = Path("input_logs.txt")

    t_start = time.perf_counter()
    records = parse_telemetry_file(log_file_path)
    generate_ascii_report(records)
    t_elapsed = time.perf_counter() - t_start

    print(f"Час виконання повного циклу аналізу тексту: {t_elapsed * 1000:.3f} мс\n")


if __name__ == "__main__":
    main()