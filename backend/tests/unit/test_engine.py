"""Unit tests for the ITR calculation engine (pure business logic, no I/O)."""
from datetime import date
from decimal import Decimal

from app.domain.engine.itr_engine import ItrCalculationEngine
from app.domain.entities.a3 import ForeignTaxCreditDetail
from app.domain.entities.fsi import ForeignSourceIncome

engine = ItrCalculationEngine()


class TestGenerateFsi:
    def test_relief_capped_by_dtaa_rate(self):
        entry = ForeignSourceIncome(
            country="UNITED_STATES_OF_AMERICA",
            income_source="Dividend",
            income_amount=Decimal("1000"),
            tax_paid_outside_india=Decimal("300"),
            tax_payable_in_india=Decimal("50000"),
            dtaa_rate=Decimal("10"),
            currency="USD",
            exchange_rate=Decimal("83"),
            assessment_year="2025-26",
        )
        rows, summary = engine.generate_fsi([entry])
        row = rows[0]

        assert row.income == Decimal("83000")
        assert row.tax_paid == Decimal("24900")
        # DTAA cap = 10% of 83000 = 8300, which is lower than tax_paid (24900) and
        # tax_payable_in_india (50000), so relief is capped at 8300.
        assert row.relief_claimed == Decimal("8300")
        assert row.net_tax == Decimal("41700")
        assert summary.row_count == 1
        assert summary.total_net_tax == Decimal("41700")

    def test_relief_capped_by_tax_payable(self):
        entry = ForeignSourceIncome(
            country="UNITED_KINGDOM",
            income_source="Interest",
            income_amount=Decimal("100"),
            tax_paid_outside_india=Decimal("40"),
            tax_payable_in_india=Decimal("100"),
            dtaa_rate=Decimal("100"),
            currency="GBP",
            exchange_rate=Decimal("100"),
            assessment_year="2025-26",
        )
        rows, _ = engine.generate_fsi([entry])
        # DTAA cap = 100% of 10000 = 10000, tax_paid_inr = 4000, tax_payable = 100
        # -> lowest of the three is tax_payable_in_india (100).
        assert rows[0].relief_claimed == Decimal("100")
        assert rows[0].net_tax == Decimal("0")


class TestGenerateA3:
    def test_uses_distinct_rates_per_valuation_point(self):
        entry = ForeignTaxCreditDetail(
            country="UNITED_STATES_OF_AMERICA",
            entity_name="Cisco Systems Inc",
            entity_address="170 West Tasman Drive San Jose CA",
            zip_code="95134",
            nature_of_entity="Company",
            acquisition_date=date(2023, 1, 15),
            currency="USD",
            initial_investment_foreign=Decimal("100"),
            peak_investment_foreign=Decimal("150"),
            closing_balance_foreign=Decimal("120"),
            sales_proceeds_foreign=Decimal("0"),
            acquisition_exchange_rate=Decimal("80"),
            peak_exchange_rate=Decimal("83"),
            closing_exchange_rate=Decimal("82"),
            dtaa_article="Article 12",
            foreign_tax_paid=Decimal("20"),
            foreign_tax_credit_claimed=Decimal("15"),
        )
        rows, summary = engine.generate_a3([entry])
        row = rows[0]
        assert row.initial_investment == Decimal("8000")
        assert row.peak_investment == Decimal("12450")
        assert row.closing_balance == Decimal("9840")
        assert row.total_gross_amount == row.initial_investment
        assert row.foreign_tax_credit_claimed == Decimal("1230")
        assert summary.row_count == 1
