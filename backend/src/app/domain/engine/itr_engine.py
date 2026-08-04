"""Default `TaxCalculationEngine` implementation.

This adapts the core arithmetic used by the existing `itr` repository
(`generate_schedule_fa_a3.py`): convert a foreign-currency amount to INR using
an applicable exchange rate, round to the nearest rupee, and treat a missing
rate as "not applicable" rather than raising. Schedule FSI relief-under-DTAA
computation (Sections 90/91 of the Income-tax Act, 1961) is added on top,
since that logic did not previously exist in the source repository.
"""
from decimal import ROUND_HALF_UP, Decimal

from app.domain.entities.a3 import A3ResultRow, A3Summary, ForeignTaxCreditDetail
from app.domain.entities.fsi import ForeignSourceIncome, FsiResultRow, FsiSummary

_ZERO = Decimal("0")


def _to_inr(amount: Decimal, rate: Decimal) -> Decimal:
    """Convert a foreign-currency amount to INR, rounded to the nearest rupee.

    Mirrors `round(quantity * price * rate)` from the original script.
    """
    return (amount * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


class ItrCalculationEngine:
    """Concrete `TaxCalculationEngine` used by the API by default."""

    def generate_fsi(
        self, input_data: list[ForeignSourceIncome]
    ) -> tuple[list[FsiResultRow], FsiSummary]:
        rows: list[FsiResultRow] = []
        for item in input_data:
            income_inr = _to_inr(item.income_amount, item.exchange_rate)
            tax_paid_inr = _to_inr(item.tax_paid_outside_india, item.exchange_rate)
            dtaa_capped_relief = (income_inr * item.dtaa_rate / Decimal(100)).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
            # Relief under DTAA (Sec. 90/91): lower of tax actually paid abroad,
            # tax payable in India on that income, and the DTAA-rate cap.
            relief_claimed = min(tax_paid_inr, item.tax_payable_in_india, dtaa_capped_relief)
            relief_claimed = max(relief_claimed, _ZERO)
            net_tax = max(item.tax_payable_in_india - relief_claimed, _ZERO)

            rows.append(
                FsiResultRow(
                    country=item.country,
                    income_source=item.income_source,
                    income=income_inr,
                    tax_paid=tax_paid_inr,
                    dtaa_rate=item.dtaa_rate,
                    relief_claimed=relief_claimed,
                    net_tax=net_tax,
                    assessment_year=item.assessment_year,
                )
            )

        summary = FsiSummary(
            total_income=sum((r.income for r in rows), _ZERO),
            total_tax_paid=sum((r.tax_paid for r in rows), _ZERO),
            total_relief_claimed=sum((r.relief_claimed for r in rows), _ZERO),
            total_net_tax=sum((r.net_tax for r in rows), _ZERO),
            row_count=len(rows),
        )
        return rows, summary

    def generate_a3(
        self, input_data: list[ForeignTaxCreditDetail]
    ) -> tuple[list[A3ResultRow], A3Summary]:
        rows: list[A3ResultRow] = []
        for item in input_data:
            initial_inr = _to_inr(item.initial_investment_foreign, item.acquisition_exchange_rate)
            peak_inr = _to_inr(item.peak_investment_foreign, item.peak_exchange_rate)
            closing_inr = _to_inr(item.closing_balance_foreign, item.closing_exchange_rate)
            sales_proceeds_inr = _to_inr(item.sales_proceeds_foreign, item.closing_exchange_rate)
            tax_credit_inr = _to_inr(
                item.foreign_tax_credit_claimed, item.closing_exchange_rate
            )

            rows.append(
                A3ResultRow(
                    country=item.country,
                    entity_name=item.entity_name,
                    entity_address=item.entity_address,
                    zip_code=item.zip_code,
                    nature_of_entity=item.nature_of_entity,
                    acquisition_date=item.acquisition_date,
                    initial_investment=initial_inr,
                    peak_investment=peak_inr,
                    closing_balance=closing_inr,
                    total_gross_amount=initial_inr,
                    sales_proceeds=sales_proceeds_inr,
                    dtaa_article=item.dtaa_article,
                    foreign_tax_credit_claimed=tax_credit_inr,
                )
            )

        summary = A3Summary(
            total_initial_investment=sum((r.initial_investment or _ZERO for r in rows), _ZERO),
            total_peak_investment=sum((r.peak_investment or _ZERO for r in rows), _ZERO),
            total_closing_balance=sum((r.closing_balance or _ZERO for r in rows), _ZERO),
            total_foreign_tax_credit_claimed=sum(
                (r.foreign_tax_credit_claimed for r in rows), _ZERO
            ),
            row_count=len(rows),
        )
        return rows, summary
