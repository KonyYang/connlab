import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MatrixContactMeasurementPlanCard } from "./MatrixContactMeasurementPlanCard";
import { DEFAULT_CONTACT_PLAN_PROFILES } from "./matrixContactMeasurementPlanSelectors";

describe("MatrixContactMeasurementPlanCard", () => {
  it("keeps specialized workbook preview and generation inline with the contact plan", () => {
    const onPreview = vi.fn();
    render(
      <MatrixContactMeasurementPlanCard
        items={[]}
        profiles={DEFAULT_CONTACT_PLAN_PROFILES}
        groupLabels={{}}
        disabled={false}
        saving={false}
        message={null}
        error={null}
        onFamilyCountChange={vi.fn()}
        onFamilyIncludedChange={vi.fn()}
        onFamilyLabelChange={vi.fn()}
        onFamilyPrefixChange={vi.fn()}
        onAddCustomFamily={vi.fn()}
        onRemoveCustomFamily={vi.fn()}
        onTargetIncludedChange={vi.fn()}
        onTargetExclusionReasonChange={vi.fn()}
        onApply={vi.fn()}
        onSave={vi.fn()}
        workbook={{
          busy: null,
          preview: {
            status: "ready",
            row_count: 4,
            sections: [{ group_label: "Group 1", source_step: "2", record_type: "llcr" }],
          },
          generated: null,
          error: null,
          canGenerate: true,
          onPreview,
          onGenerate: vi.fn(),
          onDownload: vi.fn(),
        }}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Preview specialized record" }));
    expect(onPreview).toHaveBeenCalledTimes(1);
    expect(screen.getByText("4 record rows ready")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Generate workbook" })).toBeTruthy();
    expect(screen.queryByText("Generate Test Record Draft")).toBeNull();
  });

  it("names both conflicting contact families in an inline prefix blocker", () => {
    render(
      <MatrixContactMeasurementPlanCard
        items={[]}
        profiles={DEFAULT_CONTACT_PLAN_PROFILES}
        groupLabels={{}}
        disabled={false}
        saving={false}
        message={null}
        error={null}
        onFamilyCountChange={vi.fn()}
        onFamilyIncludedChange={vi.fn()}
        onFamilyLabelChange={vi.fn()}
        onFamilyPrefixChange={vi.fn()}
        onAddCustomFamily={vi.fn()}
        onRemoveCustomFamily={vi.fn()}
        onTargetIncludedChange={vi.fn()}
        onTargetExclusionReasonChange={vi.fn()}
        onApply={vi.fn()}
        onSave={vi.fn()}
        workbook={{
          busy: null,
          preview: {
            status: "blocked",
            row_count: 0,
            sections: [],
            diagnostics: [
              {
                code: "normalized_prefix_collision",
                first_family_id: "hp",
                first_family_label: "HP",
                second_family_id: "hp_alt",
                second_family_label: "High Power duplicate",
              },
            ],
          },
          generated: null,
          error: null,
          canGenerate: false,
          onPreview: vi.fn(),
          onGenerate: vi.fn(),
          onDownload: vi.fn(),
        }}
      />
    );

    expect(
      screen.getByText("HP (hp) conflicts with High Power duplicate (hp_alt).")
    ).toBeTruthy();
  });
});
