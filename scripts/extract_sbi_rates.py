#!/usr/bin/env python3
"""
Extract SBI TT BUY rates from the sbi-fx-ratekeeper PDF forex rate cards
(https://github.com/sahilgupta/sbi-fx-ratekeeper) into one wide CSV per year:
one row per date, one column per currency holding that day's TT BUY rate, stored
at <output-dir>/<year>/sbi_tt_buy_rates.csv.

Two modes:
  scan     - read every PDF under a local pdf_files directory tree
             (<pdf-dir>/<year>/<month>/<YYYY-MM-DD>.pdf), e.g. for a one-off backfill.
  download - fetch a specific day's PDF straight from the sbi-fx-ratekeeper GitHub repo
             (raw.githubusercontent.com), e.g. for the daily GitHub Action run.

By default only dates missing from --output are processed; pass --full to
reprocess every date found (e.g. after a parsing fix).

Examples:
  # One-off backfill from a local clone of sbi-fx-ratekeeper
  python extract_sbi_rates.py scan --pdf-dir ../../sbi-fx-ratekeeper/pdf_files

  # Daily incremental update (used by the GitHub Action)
  python extract_sbi_rates.py download
"""

import argparse
import csv
import glob
import io
import os
import re
import sys
from datetime import date, datetime
from typing import Dict, List, Optional

import requests
from pypdf import PdfReader

RAW_BASE_URL = "https://raw.githubusercontent.com/sahilgupta/sbi-fx-ratekeeper/main/pdf_files"
DATE_FORMAT = "%Y-%m-%d"
DATE_COLUMN = "DATE"
CSV_FILE_NAME = "sbi_tt_buy_rates.csv"
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")

# Currency code followed by "/INR" and its rates; rates may lack a space
# between the currency code and the numbers in some PDFs.
CURRENCY_LINE_REGEX = re.compile(r"([A-Z]{3})\/INR\s*((?:\d+(?:\.\d+)?\s?)+)")


def extract_tt_buy_rates(pdf_bytes: bytes) -> Dict[str, float]:
    """Parse a SBI forex rate card PDF and return {currency: tt_buy_rate}."""
    reader = PdfReader(io.BytesIO(pdf_bytes))

    reference_text = None
    for page in reader.pages[:2]:
        page_text = page.extract_text() or ""
        if "to be used as reference rates" in page_text.lower():
            reference_text = page_text
            break
    if reference_text is None:
        raise ValueError("Reference rates table not found on the first two pages")

    rates = {}
    for line in reference_text.split("\n"):
        match = CURRENCY_LINE_REGEX.search(line)
        if match:
            currency, rates_string = match.groups()
            tt_buy = rates_string.strip().split()[0]  # TT BUY is always the first column
            rates[currency] = float(tt_buy)
    return rates


def date_from_pdf_path(pdf_path: str) -> Optional[date]:
    """Derive the rate date from a pdf_files/<year>/<month>/<YYYY-MM-DD>.pdf path."""
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    try:
        return datetime.strptime(base_name, DATE_FORMAT).date()
    except ValueError:
        return None


def year_csv_path(output_dir: str, year: int) -> str:
    return os.path.join(output_dir, str(year), CSV_FILE_NAME)


def load_existing_data(output_dir: str) -> Dict[str, Dict[str, str]]:
    """Load every <output_dir>/<year>/sbi_tt_buy_rates.csv as {date_str: {currency: rate_str}}."""
    data = {}
    for csv_path in sorted(glob.glob(os.path.join(output_dir, "*", CSV_FILE_NAME))):
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row.pop(DATE_COLUMN)
                data[date_str] = {k: v for k, v in row.items() if v}
    return data


def write_data(output_dir: str, data: Dict[str, Dict[str, str]]) -> None:
    """Write {date_str: {currency: rate}} out as one wide CSV per year, sorted by date/currency."""
    by_year: Dict[int, Dict[str, Dict[str, str]]] = {}
    for date_str, row in data.items():
        year = datetime.strptime(date_str, DATE_FORMAT).year
        by_year.setdefault(year, {})[date_str] = row

    for year, year_data in by_year.items():
        currencies = sorted({currency for row in year_data.values() for currency in row})
        header = [DATE_COLUMN] + currencies

        csv_path = year_csv_path(output_dir, year)
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for date_str in sorted(year_data):
                writer.writerow({DATE_COLUMN: date_str, **year_data[date_str]})


def scan_local_pdfs(pdf_dir: str, existing_data: Dict[str, Dict[str, str]], full: bool) -> List[tuple]:
    """Find (date, pdf_bytes) pairs to process from a local pdf_files directory tree."""
    to_process = []
    for pdf_path in sorted(glob.glob(os.path.join(pdf_dir, "**", "*.pdf"), recursive=True)):
        rate_date = date_from_pdf_path(pdf_path)
        if rate_date is None:
            print(f"Skipping {pdf_path}: filename is not a YYYY-MM-DD date", file=sys.stderr)
            continue

        date_str = rate_date.strftime(DATE_FORMAT)
        if not full and date_str in existing_data:
            continue

        with open(pdf_path, "rb") as f:
            to_process.append((date_str, f.read()))
    return to_process


def download_pdfs(dates: List[date], existing_data: Dict[str, Dict[str, str]], full: bool) -> List[tuple]:
    """Download (date, pdf_bytes) pairs from the sbi-fx-ratekeeper GitHub repo."""
    to_process = []
    for rate_date in dates:
        date_str = rate_date.strftime(DATE_FORMAT)
        if not full and date_str in existing_data:
            continue

        url = f"{RAW_BASE_URL}/{rate_date.year}/{rate_date.month}/{date_str}.pdf"
        response = requests.get(url, timeout=30)
        if response.status_code == 404:
            print(f"No PDF published yet for {date_str} ({url})", file=sys.stderr)
            continue
        response.raise_for_status()
        to_process.append((date_str, response.content))
    return to_process


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--output", "-o", default=DEFAULT_OUTPUT_DIR, help="Output directory (one CSV per year is written under it)"
    )
    common.add_argument(
        "--full", action="store_true", help="Reprocess dates already present in --output"
    )

    subparsers = parser.add_subparsers(dest="mode", required=True)

    scan_parser = subparsers.add_parser("scan", parents=[common], help="Read PDFs from a local pdf_files directory")
    scan_parser.add_argument("--pdf-dir", required=True, help="Path to a sbi-fx-ratekeeper pdf_files directory")

    download_parser = subparsers.add_parser(
        "download", parents=[common], help="Fetch PDFs from the sbi-fx-ratekeeper GitHub repo"
    )
    download_parser.add_argument(
        "--date",
        dest="dates",
        action="append",
        type=lambda s: datetime.strptime(s, DATE_FORMAT).date(),
        help=f"Date to fetch ({DATE_FORMAT}), can be repeated. Defaults to today.",
    )

    args = parser.parse_args()
    existing_data = load_existing_data(args.output)

    if args.mode == "scan":
        to_process = scan_local_pdfs(args.pdf_dir, existing_data, args.full)
    else:
        dates = args.dates or [date.today()]
        to_process = download_pdfs(dates, existing_data, args.full)

    if not to_process:
        print("No new PDFs to process.")
        return

    for date_str, pdf_bytes in to_process:
        try:
            rates = extract_tt_buy_rates(pdf_bytes)
        except Exception as e:
            print(f"Failed to parse PDF for {date_str}: {e}", file=sys.stderr)
            continue

        existing_data[date_str] = {currency: str(rate) for currency, rate in rates.items()}
        print(f"Parsed {date_str}: {len(rates)} currencies")

    write_data(args.output, existing_data)
    print(f"Wrote {len(existing_data)} dates to {args.output}")


if __name__ == "__main__":
    main()
