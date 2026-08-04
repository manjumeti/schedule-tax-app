import { MenuItem, TextField, type TextFieldProps } from "@mui/material";
import { VALID_COUNTRIES } from "@/validators/schemas";

type Props = Omit<TextFieldProps, "select" | "children">;

// Shared UI component: a validated country dropdown reused by all three entry forms.
export function CountrySelect(props: Props) {
  return (
    <TextField select label="Country" fullWidth {...props}>
      {VALID_COUNTRIES.map((country) => (
        <MenuItem key={country} value={country}>
          {country.replaceAll("_", " ")}
        </MenuItem>
      ))}
    </TextField>
  );
}
