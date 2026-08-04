import { Alert, Stack, Typography } from "@mui/material";
import type { ColumnDef } from "@tanstack/react-table";
import { A3LotForm } from "@/components/forms/A3LotForm";
import { DataTable } from "@/components/tables/DataTable";
import { useCurrentSession } from "@/context/SessionContext";
import { useCalculateA3FromLots } from "@/hooks/useA3";
import type { A3Holding, A3ResultRow } from "@/types/schedules";

const resultColumns: ColumnDef<A3ResultRow>[] = [
  { header: "Country", accessorKey: "country" },
  { header: "Name of Entity", accessorKey: "entity_name" },
  { header: "Address of Entity", accessorKey: "entity_address" },
  { header: "Zip Code", accessorKey: "zip_code" },
  { header: "Nature of Entity", accessorKey: "nature_of_entity" },
  { header: "Date of Acquisition", accessorKey: "acquisition_date" },
  { header: "Initial Investment", accessorKey: "initial_investment" },
  { header: "Peak Investment", accessorKey: "peak_investment" },
  { header: "Closing Balance", accessorKey: "closing_balance" },
  { header: "Total Gross Amount", accessorKey: "total_gross_amount" },
  { header: "Sales Proceeds", accessorKey: "sales_proceeds" },
];

export function A3Page() {
  const { sessionId } = useCurrentSession();
  const calculateFromLots = useCalculateA3FromLots();

  const handleLotsSubmit = (holding: A3Holding) => {
    calculateFromLots.mutate({ holding, sessionId });
  };

  const activeResult = calculateFromLots.data;
  const activeError = calculateFromLots.error;

  return (
    <Stack spacing={3}>
      <Typography variant="h4">Form A3 &mdash; RSU/ESPP Foreign Holdings</Typography>
      {!sessionId && (
        <Alert severity="info">
          No active session selected. Calculations will preview only; create/select a session on the
          Sessions page to persist entries.
        </Alert>
      )}
      <Alert severity="info">
        Enter each vest lot&apos;s <strong>Date Acquired, Cost and Quantity</strong> exactly as shown
        on your broker statement (e.g. an ESPP/RSU vest schedule export). Exchange rates and
        peak/closing stock prices for the year are fetched automatically &mdash; requires
        <code> APP_MARKET_DATA_PROVIDER=yfinance_sbi</code> on the backend.
      </Alert>

      <A3LotForm onSubmit={handleLotsSubmit} isSubmitting={calculateFromLots.isPending} />

      {activeError && <Alert severity="error">{(activeError as Error).message}</Alert>}

      {activeResult && (
        <>
          <Typography variant="h6">Results</Typography>
          <DataTable data={activeResult.rows} columns={resultColumns} />
          <Alert severity="success">
            Total Closing Balance: {activeResult.summary.total_closing_balance} | Total Initial
            Investment: {activeResult.summary.total_initial_investment}
          </Alert>
        </>
      )}
    </Stack>
  );
}

