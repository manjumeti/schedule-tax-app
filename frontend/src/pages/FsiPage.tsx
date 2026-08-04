import { useMemo, useState } from "react";
import { Alert, Box, Button, Stack, Typography } from "@mui/material";
import type { ColumnDef } from "@tanstack/react-table";
import { FsiEntryForm } from "@/components/forms/FsiEntryForm";
import { DataTable } from "@/components/tables/DataTable";
import { useCurrentSession } from "@/context/SessionContext";
import { useCalculateFsi } from "@/hooks/useFsi";
import type { FsiFormValues } from "@/validators/schemas";
import type { FsiResultRow } from "@/types/schedules";

const resultColumns: ColumnDef<FsiResultRow>[] = [
  { header: "Country", accessorKey: "country" },
  { header: "Income", accessorKey: "income" },
  { header: "Tax Paid", accessorKey: "tax_paid" },
  { header: "DTAA Rate", accessorKey: "dtaa_rate" },
  { header: "Relief Claimed", accessorKey: "relief_claimed" },
  { header: "Net Tax", accessorKey: "net_tax" },
];

export function FsiPage() {
  const { sessionId } = useCurrentSession();
  const [pendingEntries, setPendingEntries] = useState<FsiFormValues[]>([]);
  const calculateMutation = useCalculateFsi();

  const pendingColumns = useMemo<ColumnDef<FsiFormValues>[]>(
    () => [
      { header: "Country", accessorKey: "country" },
      { header: "Income Source", accessorKey: "income_source" },
      { header: "Income Amount", accessorKey: "income_amount" },
      { header: "Currency", accessorKey: "currency" },
      { header: "DTAA Rate", accessorKey: "dtaa_rate" },
    ],
    []
  );

  const handleAdd = (values: FsiFormValues) => setPendingEntries((prev) => [...prev, values]);

  const handleCalculate = () => {
    calculateMutation.mutate({ entries: pendingEntries, sessionId });
  };

  return (
    <Stack spacing={3}>
      <Typography variant="h4">Schedule FSI &mdash; Foreign Source Income</Typography>
      {!sessionId && (
        <Alert severity="info">
          No active session selected. Calculations will preview only; create/select a session on the
          Sessions page to persist entries.
        </Alert>
      )}

      <FsiEntryForm onAdd={handleAdd} />

      <Typography variant="h6">Pending Entries ({pendingEntries.length})</Typography>
      <DataTable data={pendingEntries} columns={pendingColumns} searchPlaceholder="Search pending entries" />

      <Box>
        <Button
          variant="contained"
          color="secondary"
          disabled={pendingEntries.length === 0 || calculateMutation.isPending}
          onClick={handleCalculate}
        >
          Calculate Schedule FSI
        </Button>
      </Box>

      {calculateMutation.isError && (
        <Alert severity="error">{(calculateMutation.error as Error).message}</Alert>
      )}

      {calculateMutation.isSuccess && (
        <>
          <Typography variant="h6">Results</Typography>
          <DataTable data={calculateMutation.data.rows} columns={resultColumns} />
          <Alert severity="success">
            Total Net Tax: {calculateMutation.data.summary.total_net_tax} | Total Relief Claimed:{" "}
            {calculateMutation.data.summary.total_relief_claimed}
          </Alert>
        </>
      )}
    </Stack>
  );
}
