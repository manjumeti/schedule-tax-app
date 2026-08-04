// Client-side validation mirrors backend rules for fast inline feedback,
// but the backend re-validates everything server-side ("never trust the client").
import { z } from "zod";

export const VALID_COUNTRIES = [
  "UNITED_STATES_OF_AMERICA",
  "UNITED_KINGDOM",
  "CANADA",
  "AUSTRALIA",
  "SINGAPORE",
  "UNITED_ARAB_EMIRATES",
  "GERMANY",
  "FRANCE",
  "NETHERLANDS",
  "SWITZERLAND",
  "JAPAN",
  "HONG_KONG",
  "MAURITIUS",
  "IRELAND",
  "LUXEMBOURG",
  "SOUTH_AFRICA",
  "NEW_ZEALAND",
  "SAUDI_ARABIA",
  "QATAR",
  "OMAN",
  "KUWAIT",
  "BAHRAIN",
  "SWEDEN",
  "NORWAY",
  "DENMARK",
  "SOUTH_KOREA",
  "CHINA",
  "MALAYSIA",
  "INDONESIA",
  "THAILAND",
] as const;

export const VALID_CURRENCIES = [
  "USD",
  "GBP",
  "EUR",
  "CAD",
  "AUD",
  "SGD",
  "AED",
  "CHF",
  "JPY",
  "HKD",
  "MUR",
  "ZAR",
  "NZD",
  "SAR",
  "QAR",
  "OMR",
  "KWD",
  "BHD",
  "SEK",
  "NOK",
  "DKK",
  "KRW",
  "CNY",
  "MYR",
  "IDR",
  "THB",
  "INR",
] as const;

const assessmentYearSchema = z
  .string()
  .regex(/^20\d{2}-\d{2}$/, "Use the form 'YYYY-YY', e.g. 2025-26");

const decimalString = z
  .string()
  .min(1, "Required")
  .refine((v) => !Number.isNaN(Number(v)), "Must be a number");

const nonNegativeDecimal = decimalString.refine((v) => Number(v) >= 0, "Must not be negative");
const positiveDecimal = decimalString.refine((v) => Number(v) > 0, "Must be greater than 0");

export const fsiEntrySchema = z
  .object({
    country: z.enum(VALID_COUNTRIES, { errorMap: () => ({ message: "Select a supported country" }) }),
    income_source: z.string().min(2, "Required"),
    income_amount: positiveDecimal,
    tax_paid_outside_india: nonNegativeDecimal,
    tax_payable_in_india: nonNegativeDecimal,
    dtaa_rate: decimalString.refine(
      (v) => Number(v) >= 0 && Number(v) <= 100,
      "Must be between 0 and 100"
    ),
    currency: z.enum(VALID_CURRENCIES),
    exchange_rate: positiveDecimal,
    assessment_year: assessmentYearSchema,
  })
  .refine((data) => Number(data.tax_paid_outside_india) <= Number(data.income_amount) * 2, {
    message: "Tax paid looks implausible relative to income (>2x)",
    path: ["tax_paid_outside_india"],
  });

export type FsiFormValues = z.infer<typeof fsiEntrySchema>;

export const a3EntrySchema = z
  .object({
    country: z.enum(VALID_COUNTRIES),
    entity_name: z.string().min(2, "Required"),
    entity_address: z.string().min(2, "Required"),
    zip_code: z.string().min(2, "Required"),
    nature_of_entity: z.string().min(2, "Required"),
    acquisition_date: z.string().refine((v) => new Date(v) <= new Date(), "Cannot be in the future"),
    currency: z.enum(VALID_CURRENCIES),
    initial_investment_foreign: nonNegativeDecimal,
    peak_investment_foreign: nonNegativeDecimal,
    closing_balance_foreign: nonNegativeDecimal,
    sales_proceeds_foreign: nonNegativeDecimal,
    acquisition_exchange_rate: positiveDecimal,
    peak_exchange_rate: positiveDecimal,
    closing_exchange_rate: positiveDecimal,
    dtaa_article: z.string().min(1, "Required"),
    foreign_tax_paid: nonNegativeDecimal,
    foreign_tax_credit_claimed: nonNegativeDecimal,
  })
  .refine((data) => Number(data.foreign_tax_credit_claimed) <= Number(data.foreign_tax_paid), {
    message: "Tax credit claimed cannot exceed foreign tax paid",
    path: ["foreign_tax_credit_claimed"],
  });

export type A3FormValues = z.infer<typeof a3EntrySchema>;

// Simple RSU/ESPP lot-based Form A3 entry: what a broker statement actually gives the user.
export const a3LotSchema = z.object({
  date_acquired: z.string().refine((v) => new Date(v) <= new Date(), "Cannot be in the future"),
  cost: positiveDecimal,
  quantity: positiveDecimal,
});

export type A3LotFormValues = z.infer<typeof a3LotSchema>;

export const a3HoldingSchema = z.object({
  country: z.enum(VALID_COUNTRIES, { errorMap: () => ({ message: "Select a supported country" }) }),
  entity_name: z.string().min(2, "Required"),
  entity_address: z.string().min(2, "Required"),
  zip_code: z.string().min(2, "Required"),
  nature_of_entity: z.string().min(2, "Required"),
  ticker: z.string().min(1, "Required").max(15).transform((v) => v.toUpperCase()),
  currency: z.enum(VALID_CURRENCIES),
});

export type A3HoldingFormValues = z.infer<typeof a3HoldingSchema>;

export const sessionMetadataSchema = z.object({
  name: z.string().min(1, "Required"),
  assessment_year: assessmentYearSchema,
});
