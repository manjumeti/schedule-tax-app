import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, Grid2 as Grid, TextField } from "@mui/material";
import { CountrySelect } from "@/components/shared/CountrySelect";
import { CurrencySelect } from "@/components/shared/CurrencySelect";
import { fsiEntrySchema, type FsiFormValues } from "@/validators/schemas";

const DEFAULTS: FsiFormValues = {
  country: "UNITED_STATES_OF_AMERICA",
  income_source: "",
  income_amount: "",
  tax_paid_outside_india: "",
  tax_payable_in_india: "",
  dtaa_rate: "",
  currency: "USD",
  exchange_rate: "",
  assessment_year: "2025-26",
};

interface Props {
  onAdd: (values: FsiFormValues) => void;
}

export function FsiEntryForm({ onAdd }: Props) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FsiFormValues>({ resolver: zodResolver(fsiEntrySchema), defaultValues: DEFAULTS });

  const onSubmit = (values: FsiFormValues) => {
    onAdd(values);
    reset(DEFAULTS);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <CountrySelect {...register("country")} error={!!errors.country} helperText={errors.country?.message} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="Income Source"
            {...register("income_source")}
            error={!!errors.income_source}
            helperText={errors.income_source?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="Assessment Year"
            placeholder="2025-26"
            {...register("assessment_year")}
            error={!!errors.assessment_year}
            helperText={errors.assessment_year?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="Income Amount"
            {...register("income_amount")}
            error={!!errors.income_amount}
            helperText={errors.income_amount?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="Tax Paid Outside India"
            {...register("tax_paid_outside_india")}
            error={!!errors.tax_paid_outside_india}
            helperText={errors.tax_paid_outside_india?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="Tax Payable In India"
            {...register("tax_payable_in_india")}
            error={!!errors.tax_payable_in_india}
            helperText={errors.tax_payable_in_india?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="DTAA Rate (%)"
            {...register("dtaa_rate")}
            error={!!errors.dtaa_rate}
            helperText={errors.dtaa_rate?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <CurrencySelect {...register("currency")} error={!!errors.currency} helperText={errors.currency?.message} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="Exchange Rate"
            {...register("exchange_rate")}
            error={!!errors.exchange_rate}
            helperText={errors.exchange_rate?.message}
          />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <Button type="submit" variant="contained">
            Add Entry
          </Button>
        </Grid>
      </Grid>
    </form>
  );
}
