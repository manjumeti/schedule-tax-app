import { zodResolver } from "@hookform/resolvers/zod";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { Button, Grid2 as Grid, IconButton, Stack, TextField, Typography } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import { CountrySelect } from "@/components/shared/CountrySelect";
import { CurrencySelect } from "@/components/shared/CurrencySelect";
import { a3HoldingSchema, a3LotSchema } from "@/validators/schemas";
import type { A3Holding } from "@/types/schedules";

const a3HoldingFormSchema = a3HoldingSchema.extend({
  lots: z.array(a3LotSchema).min(1, "Add at least one vest lot"),
});

type FormValues = z.infer<typeof a3HoldingFormSchema>;

const DEFAULTS: FormValues = {
  country: "UNITED_STATES_OF_AMERICA",
  entity_name: "",
  entity_address: "",
  zip_code: "",
  nature_of_entity: "Company",
  ticker: "",
  currency: "USD",
  lots: [{ date_acquired: new Date().toISOString().slice(0, 10), cost: "", quantity: "" }],
};

interface Props {
  onSubmit: (holding: A3Holding) => void;
  isSubmitting?: boolean;
}

export function A3LotForm({ onSubmit, isSubmitting }: Props) {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(a3HoldingFormSchema), defaultValues: DEFAULTS });

  const { fields, append, remove } = useFieldArray({ control, name: "lots" });

  const submit = (values: FormValues) => onSubmit(values as A3Holding);

  return (
    <form onSubmit={handleSubmit(submit)} noValidate>
      <Typography variant="h6" gutterBottom>
        Holding Details
      </Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <CountrySelect {...register("country")} error={!!errors.country} helperText={errors.country?.message} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="Name of Entity"
            placeholder="Cisco Systems Inc"
            {...register("entity_name")}
            error={!!errors.entity_name}
            helperText={errors.entity_name?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <TextField
            fullWidth
            label="Ticker"
            placeholder="CSCO"
            {...register("ticker")}
            error={!!errors.ticker}
            helperText={errors.ticker?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 8 }}>
          <TextField
            fullWidth
            label="Address of Entity"
            placeholder="170 West Tasman Drive San Jose CA 95134 United States"
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
            label="Nature of Entity"
            {...register("nature_of_entity")}
            error={!!errors.nature_of_entity}
            helperText={errors.nature_of_entity?.message}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <CurrencySelect {...register("currency")} error={!!errors.currency} helperText={errors.currency?.message} />
        </Grid>
      </Grid>

      <Typography variant="h6" gutterBottom>
        Vest Lots
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Enter each RSU/ESPP vest lot exactly as shown on your broker statement. Exchange rates and
        peak/closing stock prices are fetched automatically.
      </Typography>
      <Stack spacing={2} sx={{ mb: 2 }}>
        {fields.map((field, index) => (
          <Grid container spacing={2} key={field.id} alignItems="flex-start">
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="date"
                label="Date Acquired"
                InputLabelProps={{ shrink: true }}
                {...register(`lots.${index}.date_acquired`)}
                error={!!errors.lots?.[index]?.date_acquired}
                helperText={errors.lots?.[index]?.date_acquired?.message}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <TextField
                fullWidth
                label="Cost"
                {...register(`lots.${index}.cost`)}
                error={!!errors.lots?.[index]?.cost}
                helperText={errors.lots?.[index]?.cost?.message}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <TextField
                fullWidth
                label="Quantity"
                {...register(`lots.${index}.quantity`)}
                error={!!errors.lots?.[index]?.quantity}
                helperText={errors.lots?.[index]?.quantity?.message}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 2 }}>
              <IconButton
                aria-label="remove lot"
                onClick={() => remove(index)}
                disabled={fields.length === 1}
              >
                <DeleteIcon />
              </IconButton>
            </Grid>
          </Grid>
        ))}
      </Stack>
      {errors.lots?.root && (
        <Typography color="error" variant="body2" sx={{ mb: 2 }}>
          {errors.lots.root.message}
        </Typography>
      )}

      <Stack direction="row" spacing={2}>
        <Button
          startIcon={<AddIcon />}
          onClick={() => append({ date_acquired: new Date().toISOString().slice(0, 10), cost: "", quantity: "" })}
        >
          Add Lot
        </Button>
        <Button type="submit" variant="contained" disabled={isSubmitting}>
          Calculate Form A3
        </Button>
      </Stack>
    </form>
  );
}
