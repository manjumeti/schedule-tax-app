"""Service layer for CSV / PDF export of generated schedules."""
import io
from datetime import datetime, timezone
from typing import Literal

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from app.core.exceptions import NotFoundError
from app.domain.engine.interface import TaxCalculationEngine
from app.repositories.interfaces import A3Repository, FsiRepository, SessionRepository

Schedule = Literal["fsi", "a3"]

_FSI_COLUMNS = ["Country", "Income Source", "Income", "Tax Paid", "DTAA Rate", "Relief Claimed", "Net Tax"]
_A3_COLUMNS = [
    "Country",
    "Name of Entity",
    "Address of Entity",
    "Zip Code",
    "Nature of Entity",
    "Date of Acquisition",
    "Initial Investment",
    "Peak Investment",
    "Closing Balance",
    "Total Gross Amount",
    "Sales Proceeds",
]

_LARGE_LIMIT = 50_000


class ExportService:
    def __init__(
        self,
        engine: TaxCalculationEngine,
        session_repository: SessionRepository,
        fsi_repository: FsiRepository,
        a3_repository: A3Repository,
    ) -> None:
        self._engine = engine
        self._session_repository = session_repository
        self._fsi_repository = fsi_repository
        self._a3_repository = a3_repository

    async def _compute(self, session_id: str):
        session = await self._session_repository.get(session_id)
        if session is None:
            raise NotFoundError(f"Session '{session_id}' not found")

        fsi_entries, _ = await self._fsi_repository.list(session_id, 0, _LARGE_LIMIT)
        a3_entries, _ = await self._a3_repository.list(session_id, 0, _LARGE_LIMIT)

        fsi_rows, fsi_summary = self._engine.generate_fsi(fsi_entries)
        a3_rows, a3_summary = self._engine.generate_a3(a3_entries)
        return session, (fsi_rows, fsi_summary), (a3_rows, a3_summary)

    async def export_csv(self, session_id: str, schedule: Schedule) -> tuple[str, bytes]:
        _, fsi, a3 = await self._compute(session_id)

        if schedule == "fsi":
            df = pd.DataFrame(
                [
                    [r.country, r.income_source, r.income, r.tax_paid, r.dtaa_rate, r.relief_claimed, r.net_tax]
                    for r in fsi[0]
                ],
                columns=_FSI_COLUMNS,
            )
            filename = f"schedule_fsi_{session_id}.csv"
        else:
            df = pd.DataFrame(
                [
                    [
                        r.country,
                        r.entity_name,
                        r.entity_address,
                        r.zip_code,
                        r.nature_of_entity,
                        r.acquisition_date,
                        r.initial_investment,
                        r.peak_investment,
                        r.closing_balance,
                        r.total_gross_amount,
                        r.sales_proceeds,
                    ]
                    for r in a3[0]
                ],
                columns=_A3_COLUMNS,
            )
            filename = f"form_a3_{session_id}.csv"

        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        return filename, buffer.getvalue().encode("utf-8")

    async def export_pdf(self, session_id: str) -> tuple[str, bytes]:
        session, fsi, a3 = await self._compute(session_id)
        fsi_rows, fsi_summary = fsi
        a3_rows, a3_summary = a3

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=landscape(A4), topMargin=1.5 * cm, bottomMargin=1.5 * cm
        )
        styles = getSampleStyleSheet()
        elements: list = []

        elements.append(Paragraph("Indian ITR Foreign Income &amp; Assets Report", styles["Title"]))
        elements.append(
            Paragraph(
                f"Session: {session['name']} | Assessment Year: {session['assessment_year']}",
                styles["Normal"],
            )
        )
        elements.append(
            Paragraph(
                f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')} UTC",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 0.5 * cm))

        elements.append(Paragraph("Schedule FSI - Foreign Source Income", styles["Heading2"]))
        elements.append(
            self._build_table(
                _FSI_COLUMNS,
                [
                    [r.country, r.income_source, r.income, r.tax_paid, r.dtaa_rate, r.relief_claimed, r.net_tax]
                    for r in fsi_rows
                ],
            )
        )
        elements.append(
            Paragraph(
                f"Total Income: {fsi_summary.total_income} | Total Tax Paid: {fsi_summary.total_tax_paid} | "
                f"Total Relief Claimed: {fsi_summary.total_relief_claimed} | Total Net Tax: {fsi_summary.total_net_tax}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 0.5 * cm))

        elements.append(Paragraph("Form A3 - Foreign Tax Credit / DTAA Support", styles["Heading2"]))
        elements.append(
            self._build_table(
                _A3_COLUMNS,
                [
                    [
                        r.country,
                        r.entity_name,
                        r.entity_address,
                        r.zip_code,
                        r.nature_of_entity,
                        r.acquisition_date,
                        r.initial_investment,
                        r.peak_investment,
                        r.closing_balance,
                        r.total_gross_amount,
                        r.sales_proceeds,
                    ]
                    for r in a3_rows
                ],
            )
        )
        elements.append(
            Paragraph(
                f"Total Initial Investment: {a3_summary.total_initial_investment} | "
                f"Total Peak Investment: {a3_summary.total_peak_investment} | "
                f"Total Closing Balance: {a3_summary.total_closing_balance} | "
                f"Total Foreign Tax Credit Claimed: {a3_summary.total_foreign_tax_credit_claimed}",
                styles["Normal"],
            )
        )

        doc.build(elements)
        return f"itr_foreign_report_{session_id}.pdf", buffer.getvalue()

    @staticmethod
    def _build_table(columns: list[str], rows: list[list]) -> Table:
        data = [columns] + [[str(cell) for cell in row] for row in rows] if rows else [columns]
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
                ]
            )
        )
        return table
