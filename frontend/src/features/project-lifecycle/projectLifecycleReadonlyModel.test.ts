import { describe, expect, it } from "vitest";
import {
  deriveProjectLifecycleReadonlyView,
  deriveReadonlyApiErrorMessage,
} from "./projectLifecycleReadonlyModel";

describe("project lifecycle readonly model", () => {
  it("keeps active projects writable", () => {
    const view = deriveProjectLifecycleReadonlyView({
      project_id: "P1",
      lifecycle_state: "active",
      closure_type: null,
      status_label: "Active",
      readonly: false,
      allowed_actions: [],
      status: "ltr_registered",
      warnings: [],
    });

    expect(view.mode).toBe("active");
    expect(view.canWriteBusinessData).toBe(true);
    expect(view.canUseReadonlyPreview).toBe(true);
  });

  it("marks stopped projects readonly with activate guidance", () => {
    const view = deriveProjectLifecycleReadonlyView({
      project_id: "P1",
      lifecycle_state: "stopped",
      closure_type: null,
      status_label: "Stopped",
      readonly: true,
      allowed_actions: ["activate", "resume", "close"],
      status: "cancelled",
      warnings: [],
    });

    expect(view.mode).toBe("stopped_readonly");
    expect(view.canResume).toBe(false);
    expect(view.canClose).toBe(true);
    expect(view.canWriteBusinessData).toBe(false);
    expect(view.message).toContain("Activate it before making changes");
  });

  it("marks completed close as activatable readonly", () => {
    const view = deriveProjectLifecycleReadonlyView({
      project_id: "P1",
      lifecycle_state: "closed",
      closure_type: "completed",
      close_reason_category: "completed",
      close_reason_label: "Completed",
      status_label: "Closed",
      readonly: true,
      allowed_actions: ["activate"],
      status: "closed",
      warnings: [],
    });

    expect(view.mode).toBe("closed_readonly");
    expect(view.canResume).toBe(false);
    expect(view.canClose).toBe(false);
    expect(view.title).toBe("Project closed: Completed");
    expect(view.message).toContain("Activate it before making changes");
  });

  it("maps legacy non-completed close to business readonly copy", () => {
    const view = deriveProjectLifecycleReadonlyView({
      project_id: "P1",
      lifecycle_state: "closed",
      closure_type: "administrative",
      close_reason_category: "other",
      close_reason_label: "Other",
      status_label: "Closed",
      readonly: true,
      allowed_actions: ["activate"],
      status: "closed",
      warnings: [],
    });

    expect(view.mode).toBe("closed_readonly");
    expect(view.canResume).toBe(false);
    expect(view.title).toBe("Project closed: Other");
    expect(view.message).not.toMatch(/administrative|archived/i);
  });

  it("maps TASK_338 readonly detail to business copy", () => {
    expect(
      deriveReadonlyApiErrorMessage({
        code: "project_lifecycle_readonly",
        project_id: "P1",
        lifecycle_state: "closed",
        closure_type: "administrative",
        close_reason_category: "other",
        close_reason_label: "Other",
        message: "This project is closed administratively and is readonly.",
        allowed_actions: ["activate"],
      })
    ).toBe("This project is closed. Activate it before making changes.");
  });
});
