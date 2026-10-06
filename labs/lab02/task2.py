import argparse
import json
import logging
import re
from collections import Counter
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("PIIScanner")


PATTERNS = {
    "cards": r"\b(?:\d[ -]*?){13,16}\b",
    "emails": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
    "phones": r"(?:\+\d{1,3}[ -]?)?\(?\d{2,4}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|\b0\d{9}\b",
    "ips": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
}


def mask_value(val: str, pii_type: str) -> str:

    if pii_type == "cards":
        digits = re.sub(r"\D", "", val)
        if len(digits) >= 12:
            return f"{digits[:4]}-****-****-{digits[-4:]}"
        return "****-****-****-****"

    elif pii_type == "emails":
        parts = val.split("@")
        if len(parts) == 2:
            name, domain = parts
            masked_name = name[0] + "***" if len(name) > 1 else "*"
            return f"{masked_name}@{domain}"
        return "***@***"

    elif pii_type == "phones":
        digits = re.sub(r"\D", "", val)
        if len(digits) >= 7:
            return f"{digits[:3]}-***-**-{digits[-2:]}"
        return "***-***-***"

    elif pii_type == "ips":
        octets = val.split(".")
        if len(octets) == 4:
            return f"{octets[0]}.{octets[1]}.***.***"
        return "*.*.*.*"

    return "*****"


def scan_file(file_path: Path, active_patterns: dict, apply_mask: bool):

    file_findings = []
    file_counts = Counter()

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Не вдалося прочитати файл {file_path}: {e}")
        return file_findings, file_counts

    for line_num, line in enumerate(content.splitlines(), start=1):
        for pii_type, pattern in active_patterns.items():
            matches = re.findall(pattern, line)
            for raw_val in matches:

                if pii_type == "ips":
                    parts = raw_val.split(".")
                    if any(int(p) > 255 for p in parts if p.isdigit()):
                        continue

                file_counts[pii_type] += 1
                display_val = mask_value(raw_val, pii_type) if apply_mask else raw_val

                file_findings.append({
                    "line": line_num,
                    "type": pii_type,
                    "raw_or_masked": display_val
                })

    if file_findings:
        logger.warning(f"Знайдено PII у файлі {file_path}: {dict(file_counts)}")

    return file_findings, file_counts


def scan_directory(scan_dir: str, pattern_choice: str, apply_mask: bool) -> tuple[dict, Counter]:

    dir_path = Path(scan_dir)
    if not dir_path.exists() or not dir_path.is_dir():
        logger.error(f"Вказана директорія не існує: {scan_dir}")
        return {}, Counter()


    if pattern_choice == "cards":
        active_patterns = {"cards": PATTERNS["cards"]}
    elif pattern_choice == "emails":
        active_patterns = {"emails": PATTERNS["emails"]}
    else:
        active_patterns = PATTERNS

    all_results = {}
    total_counter = Counter()


    for file_path in dir_path.rglob("*"):
        if file_path.is_file():
            findings, counts = scan_file(file_path, active_patterns, apply_mask)
            if findings:
                all_results[str(file_path)] = findings
                total_counter.update(counts)

    return all_results, total_counter


def main():
    parser = argparse.ArgumentParser(description="PII  Scanner — Сканер витоків конфіденційних даних")
    parser.add_argument("--scan-dir", required=True, help="Директорія для рекурсивного сканування")
    parser.add_argument("--patterns", choices=["all", "cards", "emails"], default="all", help="Типи даних для пошуку")
    parser.add_argument("--mask", action="store_true", help="Прапорець для маскування знайдених PII")
    parser.add_argument("--out-json", help="Шлях до файлу підсумкового JSON-звіту")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print(" STARTING PII  SCANNER")
    print(f" Directory: {args.scan_dir}")
    print(f" Mode: {args.patterns} | Masking: {args.mask}")
    print("=" * 60 + "\n")

    findings_by_file, total_counts = scan_directory(args.scan_dir, args.patterns, args.mask)

    print("\n" + "=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)
    print(f"Total sensitive items found: {sum(total_counts.values())}")
    for pii_type, count in total_counts.items():
        print(f"  - {pii_type.upper()}: {count}")
    print("=" * 60)


    report = {
        "scan_directory": args.scan_dir,
        "pattern_mode": args.patterns,
        "masked": args.mask,
        "total_summary": dict(total_counts),
        "details": findings_by_file,
    }

    if args.out_json:
        out_path = Path(args.out_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"Звіт успішно збережено в: {out_path}")


if __name__ == "__main__":
    main()