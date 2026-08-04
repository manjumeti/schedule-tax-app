"""Unit tests for Pydantic v2 DTO validation rules."""
import pytest
from pydantic import ValidationError

from app.dto.a3 import A3EntryRequest
from app.dto.fsi import FsiEntryRequest

VALID_FSI = dict(
    country="United States Of America",
    income_source="Dividend",
    income_amount="1000",
    tax_paid_outside_india="100",
    tax_payable_in_india="500",
    dtaa_rate="10",
    currency="usd",
    exchange_rate="83",
    assessment_year="2025-26",
)

class TestFsiValidation:
    def test_valid_entry_normalizes_country_and_currency(self):
        entry = FsiEntryRequest(**VALID_FSI)
        assert entry.country == "UNITED_STATES_OF_AMERICA"
        assert entry.currency == "USD"

    def test_invalid_country_rejected(self):
        with pytest.raises(ValidationError):
            FsiEntryRequest(**{**VALID_FSI, "country": "Narnia"})

    def test_invalid_currency_rejected(self):
        with pytest.raises(ValidationError):
            FsiEntryRequest(**{**VALID_FSI, "currency": "XXX"})

    def test_dtaa_rate_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            FsiEntryRequest(**{**VALID_FSI, "dtaa_rate": "150"})

    def test_malformed_assessment_year_rejected(self):
        with pytest.raises(ValidationError):
            FsiEntryRequest(**{**VALID_FSI, "assessment_year": "2025"})

    def test_implausible_tax_paid_rejected(self):
        with pytest.raises(ValidationError):
            FsiEntryRequest(**{**VALID_FSI, "tax_paid_outside_india": "5000"})

    def test_negative_income_rejected(self):
        with pytest.raises(ValidationError):
            FsiEntryRequest(**{**VALID_FSI, "income_amount": "-1"})


class TestA3Validation:
    def test_tax_credit_exceeding_tax_paid_rejected(self):
        with pytest.raises(ValidationError):
            A3EntryRequest(
                country="United States Of America",
                entity_name="Cisco Systems Inc",
                entity_address="170 West Tasman Drive",
                zip_code="95134",
                nature_of_entity="Company",
                acquisition_date="2023-01-15",
                currency="usd",
                initial_investment_foreign="100",
                peak_investment_foreign="150",
                closing_balance_foreign="120",
                acquisition_exchange_rate="80",
                peak_exchange_rate="83",
                closing_exchange_rate="82",
                dtaa_article="Article 12",
                foreign_tax_paid="10",
                foreign_tax_credit_claimed="20",
            )
