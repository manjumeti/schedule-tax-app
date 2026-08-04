"""Shared DTO building blocks: reference data and reusable validators.

Country/currency lists are intentionally curated (not exhaustive ISO lists)
to focus on jurisdictions relevant to Indian DTAA/FA reporting; extend as needed.
"""
import re
from decimal import Decimal

VALID_COUNTRIES: set[str] = {
    "UNITED_STATES_OF_AMERICA",
    "UNITED_KINGDOM",
    "CANADA",
    "AUSTRALIA",
    "SINGAPORE",
    "UNITED_ARAB_EMIRATES",
    "GERMANY",
    "FRANCE",
    "NETHERLANDS",
    "SWITZERLAND",
    "JAPAN",
    "HONG_KONG",
    "MAURITIUS",
    "IRELAND",
    "LUXEMBOURG",
    "SOUTH_AFRICA",
    "NEW_ZEALAND",
    "SAUDI_ARABIA",
    "QATAR",
    "OMAN",
    "KUWAIT",
    "BAHRAIN",
    "SWEDEN",
    "NORWAY",
    "DENMARK",
    "SOUTH_KOREA",
    "CHINA",
    "MALAYSIA",
    "INDONESIA",
    "THAILAND",
}

VALID_CURRENCIES: set[str] = {
    "USD",
    "GBP",
    "EUR",
    "CAD",
    "AUD",
    "SGD",
    "AED",
    "CHF",
    "JPY",
    "HKD",
    "MUR",
    "ZAR",
    "NZD",
    "SAR",
    "QAR",
    "OMR",
    "KWD",
    "BHD",
    "SEK",
    "NOK",
    "DKK",
    "KRW",
    "CNY",
    "MYR",
    "IDR",
    "THB",
    "INR",
}

_ASSESSMENT_YEAR_PATTERN = re.compile(r"^(20\d{2})-(\d{2})$")


def validate_country(value: str) -> str:
    normalized = value.strip().upper().replace(" ", "_")
    if normalized not in VALID_COUNTRIES:
        raise ValueError(
            f"Unknown/unsupported country code '{value}'. "
            f"Expected one of the supported DTAA jurisdictions."
        )
    return normalized


def validate_currency(value: str) -> str:
    normalized = value.strip().upper()
    if normalized not in VALID_CURRENCIES:
        raise ValueError(f"Unsupported currency code '{value}'.")
    return normalized


def validate_assessment_year(value: str) -> str:
    match = _ASSESSMENT_YEAR_PATTERN.match(value.strip())
    if not match:
        raise ValueError("Assessment year must be in the form 'YYYY-YY', e.g. '2025-26'.")
    start_year = int(match.group(1))
    end_suffix = int(match.group(2))
    if (start_year + 1) % 100 != end_suffix:
        raise ValueError("Assessment year range is not consecutive, e.g. use '2025-26'.")
    return value.strip()


def validate_positive(value: Decimal, field_name: str = "value") -> Decimal:
    if value < 0:
        raise ValueError(f"{field_name} must not be negative.")
    return value


def validate_percentage(value: Decimal, field_name: str = "rate") -> Decimal:
    if value < 0 or value > 100:
        raise ValueError(f"{field_name} must be between 0 and 100.")
    return value
