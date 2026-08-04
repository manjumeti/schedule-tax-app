import { describe, expect, it } from "vitest";
import { fsiEntrySchema, a3EntrySchema } from "@/validators/schemas";

describe("fsiEntrySchema", () => {
  const valid = {
    country: "UNITED_STATES_OF_AMERICA",
    income_source: "Dividend",
    income_amount: "1000",
    tax_paid_outside_india: "100",
    tax_payable_in_india: "150",
    dtaa_rate: "15",
    currency: "USD",
    exchange_rate: "83.5",
    assessment_year: "2025-26",
  };

  it("accepts a valid entry", () => {
    expect(fsiEntrySchema.safeParse(valid).success).toBe(true);
  });

  it("rejects a negative income amount", () => {
    const result = fsiEntrySchema.safeParse({ ...valid, income_amount: "-5" });
    expect(result.success).toBe(false);
  });

  it("rejects tax paid that is implausibly higher than income", () => {
    const result = fsiEntrySchema.safeParse({ ...valid, tax_paid_outside_india: "5000" });
    expect(result.success).toBe(false);
  });

  it("rejects malformed assessment year", () => {
    const result = fsiEntrySchema.safeParse({ ...valid, assessment_year: "2025" });
    expect(result.success).toBe(false);
  });
});

describe("a3EntrySchema", () => {
  const valid = {
    country: "UNITED_STATES_OF_AMERICA",
    entity_name: "Acme Inc",
    entity_address: "123 Main St",
    zip_code: "94000",
    nature_of_entity: "Company",
    acquisition_date: "2022-01-01",
    currency: "USD",
    initial_investment_foreign: "1000",
    peak_investment_foreign: "2000",
    closing_balance_foreign: "1500",
    sales_proceeds_foreign: "0",
    acquisition_exchange_rate: "80",
    peak_exchange_rate: "82",
    closing_exchange_rate: "83",
    dtaa_article: "Article 10",
    foreign_tax_paid: "100",
    foreign_tax_credit_claimed: "50",
  };

  it("accepts a valid entry", () => {
    expect(a3EntrySchema.safeParse(valid).success).toBe(true);
  });

  it("rejects tax credit claimed greater than tax paid", () => {
    const result = a3EntrySchema.safeParse({ ...valid, foreign_tax_credit_claimed: "500" });
    expect(result.success).toBe(false);
  });
});
