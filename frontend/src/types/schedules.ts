// Shared TypeScript types mirroring backend DTOs (app/dto/*.py).
// Decimal values are transported as strings by FastAPI/Pydantic JSON encoding,
// so numeric fields here are typed as `string` and parsed for display/math.

export interface FsiEntry {
  country: string;
  income_source: string;
  income_amount: string;
  tax_paid_outside_india: string;
  tax_payable_in_india: string;
  dtaa_rate: string;
  currency: string;
  exchange_rate: string;
  assessment_year: string;
}

export interface FsiResultRow {
  country: string;
  income_source: string;
  income: string;
  tax_paid: string;
  dtaa_rate: string;
  relief_claimed: string;
  net_tax: string;
  assessment_year: string;
}

export interface FsiSummary {
  total_income: string;
  total_tax_paid: string;
  total_relief_claimed: string;
  total_net_tax: string;
  row_count: number;
}

export interface A3Entry {
  country: string;
  entity_name: string;
  entity_address: string;
  zip_code: string;
  nature_of_entity: string;
  acquisition_date: string;
  currency: string;
  initial_investment_foreign: string;
  peak_investment_foreign: string;
  closing_balance_foreign: string;
  sales_proceeds_foreign: string;
  acquisition_exchange_rate: string;
  peak_exchange_rate: string;
  closing_exchange_rate: string;
  dtaa_article: string;
  foreign_tax_paid: string;
  foreign_tax_credit_claimed: string;
}

export interface A3ResultRow {
  country: string;
  entity_name: string;
  entity_address: string;
  zip_code: string;
  nature_of_entity: string;
  acquisition_date: string;
  initial_investment: string | null;
  peak_investment: string | null;
  closing_balance: string | null;
  total_gross_amount: string | null;
  sales_proceeds: string;
  dtaa_article: string;
  foreign_tax_credit_claimed: string;
}

export interface A3Summary {
  total_initial_investment: string;
  total_peak_investment: string;
  total_closing_balance: string;
  total_foreign_tax_credit_claimed: string;
  row_count: number;
}

// RSU/ESPP vest lot: what a broker statement actually gives the user.
export interface A3Lot {
  date_acquired: string;
  cost: string;
  quantity: string;
}

export interface A3Holding {
  country: string;
  entity_name: string;
  entity_address: string;
  zip_code: string;
  nature_of_entity: string;
  ticker: string;
  currency: string;
  lots: A3Lot[];
}

export interface SessionSummary {
  id: string;
  name: string;
  assessment_year: string;
  created_at: string;
  updated_at: string;
  fsi_count: number;
  a3_count: number;
}

export interface SessionDetail {
  id: string;
  name: string;
  assessment_year: string;
  created_at: string;
  updated_at: string;
  fsi_entries: FsiEntry[];
  a3_entries: A3Entry[];
}

export interface DashboardData {
  session_id: string;
  total_foreign_accounts: number;
  total_dividend_income: string;
  total_tax_paid_outside_india: string;
  generated_schedules: string[];
  validation_status: {
    is_valid: boolean;
    error_count: number;
    warning_count: number;
  };
}

export interface ApiErrorPayload {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
}
