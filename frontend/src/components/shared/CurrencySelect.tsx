import { MenuItem, TextField, type TextFieldProps } from "@mui/material";
import { VALID_CURRENCIES } from "@/validators/schemas";

type Props = Omit<TextFieldProps, "select" | "children">;

export function CurrencySelect(props: Props) {
  return (
    <TextField select label="Currency" fullWidth {...props}>
      {VALID_CURRENCIES.map((currency) => (
        <MenuItem key={currency} value={currency}>
          {currency}
        </MenuItem>
      ))}
    </TextField>
  );
}
