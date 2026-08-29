import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TestReportDraftButton } from "./TestReportDraftButton";

describe("TestReportDraftButton", () => {
  it("opens Report Workspace instead of generating a report immediately", () => {
    const onOpen = vi.fn();
    render(<TestReportDraftButton onOpen={onOpen} />);

    fireEvent.click(screen.getByRole("button", { name: "Test Report" }));

    expect(onOpen).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("button", { name: "Test Report" }).hasAttribute("disabled")).toBe(false);
  });
});
