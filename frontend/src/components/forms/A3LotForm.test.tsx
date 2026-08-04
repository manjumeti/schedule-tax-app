import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { A3LotForm } from "@/components/forms/A3LotForm";

describe("A3LotForm", () => {
  it("rejects submission when required holding fields are missing", async () => {
    const onSubmit = vi.fn();
    render(<A3LotForm onSubmit={onSubmit} />);

    await userEvent.click(screen.getByRole("button", { name: /calculate form a3/i }));

    expect(await screen.findAllByText(/required/i)).not.toHaveLength(0);
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits holding metadata with the default lot filled in", async () => {
    const onSubmit = vi.fn();
    render(<A3LotForm onSubmit={onSubmit} />);

    await userEvent.type(screen.getByPlaceholderText(/cisco systems inc/i), "Cisco Systems Inc");
    await userEvent.type(screen.getByPlaceholderText(/^CSCO$/), "CSCO");
    await userEvent.type(
      screen.getByPlaceholderText(/170 west tasman/i),
      "170 West Tasman Drive San Jose CA 95134"
    );
    await userEvent.type(screen.getByLabelText(/zip code/i), "95134");
    await userEvent.type(screen.getByLabelText(/cost/i), "2121.34");
    await userEvent.type(screen.getByLabelText(/quantity/i), "41");

    await userEvent.click(screen.getByRole("button", { name: /calculate form a3/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const holding = onSubmit.mock.calls[0][0];
    expect(holding.ticker).toBe("CSCO");
    expect(holding.lots).toHaveLength(1);
  });

  it("supports adding an additional lot row", async () => {
    const onSubmit = vi.fn();
    render(<A3LotForm onSubmit={onSubmit} />);

    await userEvent.click(screen.getByRole("button", { name: /add lot/i }));

    expect(screen.getAllByLabelText(/^cost$/i)).toHaveLength(2);
  });
});
