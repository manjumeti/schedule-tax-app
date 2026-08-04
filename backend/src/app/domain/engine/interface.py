"""The calculation-engine boundary.

Everything above this interface (API, services) depends only on the
`TaxCalculationEngine` Protocol, never on a concrete implementation. This lets
the existing `itr` repository's logic be plugged in today, and lets it be
swapped for a different engine later (e.g. a rules-engine or an external
microservice) without touching the API or the frontend contract.
"""
from typing import Protocol

from app.domain.entities.a3 import A3ResultRow, A3Summary, ForeignTaxCreditDetail
from app.domain.entities.fsi import ForeignSourceIncome, FsiResultRow, FsiSummary


class TaxCalculationEngine(Protocol):
    """Contract every calculation engine implementation must satisfy."""

    def generate_fsi(
        self, input_data: list[ForeignSourceIncome]
    ) -> tuple[list[FsiResultRow], FsiSummary]: ...

    def generate_a3(
        self, input_data: list[ForeignTaxCreditDetail]
    ) -> tuple[list[A3ResultRow], A3Summary]: ...
