import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, Grid2 as Grid, TextField } from "@mui/material";
import { CountrySelect } from "@/components/shared/CountrySelect";
import { CurrencySelect } from "@/components/shared/CurrencySelect";
import { a3EntrySchema, type A3FormValues } from "@/validators/schemas";

const DEFAULTS: A3FormValues = {
  country: "UNITED_STATES_OF_AMERICA",
  entity_name: "",
  entity_address: "",
  zip_code: "",
  nature_of_entity: "Company",
  acquisition_date: new Date().toISOString().slice(0, 10),
  currency: "USD",
  initial_investment_foreign: "",
  peak_investment_foreign: "",
  closing_balance_foreign: "",
  sales_proceeds_foreign: "0",
  acquisition_exchange_rate: "",
  peak_exchange_rate: "",
  closing_exchange_rate: "",
  dtaa_article: "",
  foreign_tax_paid: "0",
  foreign_tax_credit_claimed: "0",
};

interface Props {
  onAdd: (values: A3FormValues) => void;
}

export function A3EntryForm({ onAdd }: Props) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<A3FormValues>({ resolver: zodResolver(a3EntrySchema), defaultValues: DEFAULTS });

  const onSubmit = (values: A3FormValues) => {
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
            label="Entity Name"
            {...register("entity_name")}
            error={!!errors.entity_name}
            helperText={errors.entity_name?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="Nature of Entity"
            {...register("nature_of_entity")}
            error={!!errors.nature_of_entity}
            helperText={errors.nature_of_entity?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 8 }}>
          <TextField
            fullWidth
            label="Entity Address"
            {...register("entity_address")}
            error={!!errors.entity_address}
            helperText={errors.entity_address?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 4 }}>
          <TextField
            fullWidth
            label="Zip Code"
            {...register("zip_code")}
            error={!!errors.zip_code}
            helperText={errors.zip_code?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            type="date"
            label="Date of Acquisition"
            InputLabelProps={{ shrink: true }}
            {...register("acquisition_date")}
            error={!!errors.acquisition_date}
            helperText={errors.acquisition_date?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <CurrencySelect {...register("currency")} error={!!errors.currency} helperText={errors.currency?.message} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="DTAA Article"
            {...register("dtaa_article")}
            error={!!errors.dtaa_article}
            helperText={errors.dtaa_article?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            label="Initial Investment (Foreign)"
            {...register("initial_investment_foreign")}
            error={!!errors.initial_investment_foreign}
            helperText={errors.initial_investment_foreign?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            label="Peak Investment (Foreign)"
            {...register("peak_investment_foreign")}
            error={!!errors.peak_investment_foreign}
            helperText={errors.peak_investment_foreign?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            label="Closing Balance (Foreign)"
            {...register("closing_balance_foreign")}
            error={!!errors.closing_balance_foreign}
            helperText={errors.closing_balance_foreign?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            label="Sales Proceeds (Foreign)"
            {...register("sales_proceeds_foreign")}
            error={!!errors.sales_proceeds_foreign}
            helperText={errors.sales_proceeds_foreign?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            label="Acquisition Exchange Rate"
            {...register("acquisition_exchange_rate")}
            error={!!errors.acquisition_exchange_rate}
            helperText={errors.acquisition_exchange_rate?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            label="Peak Exchange Rate"
            {...register("peak_exchange_rate")}
            error={!!errors.peak_exchange_rate}
            helperText={errors.peak_exchange_rate?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            label="Closing Exchange Rate"
            {...register("closing_exchange_rate")}
            error={!!errors.closing_exchange_rate}
            helperText={errors.closing_exchange_rate?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            label="Foreign Tax Paid"
            {...register("foreign_tax_paid")}
            error={!!errors.foreign_tax_paid}
            helperText={errors.foreign_tax_paid?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            label="Foreign Tax Credit Claimed"
            {...register("foreign_tax_credit_claimed")}
            error={!!errors.foreign_tax_credit_claimed}
            helperText={errors.foreign_tax_credit_claimed?.message}
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
