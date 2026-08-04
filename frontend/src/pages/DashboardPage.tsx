import { useEffect, useState } from "react";
import { Alert, Box, Button, Card, CardContent, Chip, Grid2 as Grid, Stack, Typography } from "@mui/material";
import type { ColumnDef } from "@tanstack/react-table";
import { DataTable } from "@/components/tables/DataTable";
import { useCurrentSession } from "@/context/SessionContext";
import { useDashboard } from "@/hooks/useDashboard";
import { useFsiEntries } from "@/hooks/useFsi";
import { useA3Entries } from "@/hooks/useA3";
import { exportService } from "@/services/exportService";
import type { A3Entry, FsiEntry } from "@/types/schedules";

type ScheduleKey = "fsi" | "a3";

const SCHEDULE_LABEL_TO_KEY: Record<string, ScheduleKey> = {
  "Schedule FSI": "fsi",
  "Form A3": "a3",
};

const SCHEDULE_KEY_TO_LABEL: Record<ScheduleKey, string> = {
  fsi: "Schedule FSI",
  a3: "Form A3",
};

const fsiColumns: ColumnDef<FsiEntry>[] = [
  { header: "Country", accessorKey: "country" },
  { header: "Income Source", accessorKey: "income_source" },
  { header: "Income Amount", accessorKey: "income_amount" },
  { header: "Tax Paid Outside India", accessorKey: "tax_paid_outside_india" },
  { header: "Currency", accessorKey: "currency" },
  { header: "DTAA Rate", accessorKey: "dtaa_rate" },
];

const a3Columns: ColumnDef<A3Entry>[] = [
  { header: "Country", accessorKey: "country" },
  { header: "Name of Entity", accessorKey: "entity_name" },
  { header: "Date of Acquisition", accessorKey: "acquisition_date" },
  { header: "Currency", accessorKey: "currency" },
  { header: "Initial Investment", accessorKey: "initial_investment_foreign" },
  { header: "Peak Investment", accessorKey: "peak_investment_foreign" },
  { header: "Closing Balance", accessorKey: "closing_balance_foreign" },
  { header: "Sales Proceeds", accessorKey: "sales_proceeds_foreign" },
];

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h5">{value}</Typography>
      </CardContent>
    </Card>
  );
}

function ScheduleDataView({ sessionId, scheduleKey }: { sessionId: string; scheduleKey: ScheduleKey }) {
  const fsiQuery = useFsiEntries(scheduleKey === "fsi" ? sessionId : undefined);
  const a3Query = useA3Entries(scheduleKey === "a3" ? sessionId : undefined);

  if (scheduleKey === "fsi") {
    if (fsiQuery.isLoading) return <Typography>Loading Schedule FSI entries...</Typography>;
    if (fsiQuery.isError) return <Alert severity="error">Failed to load Schedule FSI entries</Alert>;
    return <DataTable data={fsiQuery.data?.items ?? []} columns={fsiColumns} searchPlaceholder="Search Schedule FSI entries" />;
  }

  if (a3Query.isLoading) return <Typography>Loading Form A3 entries...</Typography>;
  if (a3Query.isError) return <Alert severity="error">Failed to load Form A3 entries</Alert>;
  return <DataTable data={a3Query.data?.items ?? []} columns={a3Columns} searchPlaceholder="Search Form A3 entries" />;
}

export function DashboardPage() {
  const { sessionId } = useCurrentSession();
  const { data, isLoading, isError, error } = useDashboard(sessionId);
  const [selectedSchedule, setSelectedSchedule] = useState<ScheduleKey | null>(null);

  const availableKeys = data?.generated_schedules
    .map((label) => SCHEDULE_LABEL_TO_KEY[label])
    .filter((key): key is ScheduleKey => Boolean(key));
  const availableKeysSignature = availableKeys?.join(",") ?? "";

  useEffect(() => {
    if (!availableKeys) return;
    if (selectedSchedule && availableKeys.includes(selectedSchedule)) return;
    setSelectedSchedule(availableKeys[0] ?? null);
  }, [availableKeysSignature]);

  if (!sessionId) {
    return (
      <Alert severity="info">
        Select or create a session on the Sessions page to view the dashboard.
      </Alert>
    );
  }

  if (isLoading) {
    return <Typography>Loading dashboard...</Typography>;
  }

  if (isError || !data) {
    return <Alert severity="error">{(error as Error)?.message ?? "Failed to load dashboard"}</Alert>;
  }

  return (
    <Stack spacing={3}>
      <Typography variant="h4">Dashboard</Typography>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard label="Total Foreign Accounts" value={data.total_foreign_accounts} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard label="Total Dividend/FSI Income" value={data.total_dividend_income} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard label="Total Tax Paid Outside India" value={data.total_tax_paid_outside_india} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            label="Validation Status"
            value={data.validation_status.is_valid ? "Valid" : "Has Issues"}
          />
        </Grid>
      </Grid>

      <Box>
        <Typography variant="subtitle1" gutterBottom>
          Export
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            disabled={!selectedSchedule}
            onClick={() => selectedSchedule && exportService.downloadCsv(sessionId, selectedSchedule)}
          >
            {selectedSchedule
              ? `Export ${SCHEDULE_KEY_TO_LABEL[selectedSchedule]} CSV`
              : "Select a report below to export"}
          </Button>
          <Button variant="contained" onClick={() => exportService.downloadPdf(sessionId)}>
            Export Full Report (PDF)
          </Button>
        </Stack>
      </Box>

      <Box>
        <Typography variant="subtitle1" gutterBottom>
          Generated Reports
        </Typography>
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          {data.generated_schedules.length === 0 && (
            <Typography color="text.secondary">None yet</Typography>
          )}
          {data.generated_schedules.map((label) => {
            const key = SCHEDULE_LABEL_TO_KEY[label];
            return (
              <Chip
                key={label}
                label={label}
                color="primary"
                variant={selectedSchedule === key ? "filled" : "outlined"}
                onClick={key ? () => setSelectedSchedule(key) : undefined}
                clickable={Boolean(key)}
              />
            );
          })}
        </Stack>

        {selectedSchedule && <ScheduleDataView sessionId={sessionId} scheduleKey={selectedSchedule} />}
      </Box>
    </Stack>
  );
}
