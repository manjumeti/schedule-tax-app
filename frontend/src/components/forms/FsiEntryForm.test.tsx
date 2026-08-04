import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FsiEntryForm } from "@/components/forms/FsiEntryForm";

describe("FsiEntryForm", () => {
  it("shows a validation error when required fields are missing", async () => {
    const onAdd = vi.fn();
    render(<FsiEntryForm onAdd={onAdd} />);

    await userEvent.click(screen.getByRole("button", { name: /add entry/i }));

    expect(await screen.findAllByText(/required/i)).not.toHaveLength(0);
    expect(onAdd).not.toHaveBeenCalled();
  });

  it("submits valid data and resets the form", async () => {
    const onAdd = vi.fn();
    render(<FsiEntryForm onAdd={onAdd} />);

    await userEvent.type(screen.getByLabelText(/income source/i), "Dividend");
    await userEvent.type(screen.getByLabelText(/income amount/i), "1000");
    await userEvent.type(screen.getByLabelText(/tax paid outside india/i), "100");
    await userEvent.type(screen.getByLabelText(/tax payable in india/i), "150");
    await userEvent.type(screen.getByLabelText(/dtaa rate/i), "15");
    await userEvent.type(screen.getByLabelText(/exchange rate/i), "83.5");

    await userEvent.click(screen.getByRole("button", { name: /add entry/i }));

    expect(onAdd).toHaveBeenCalledTimes(1);
  });
});
