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

  it("marks stopped projects readonly with resume guidance", () => {
    const view = deriveProjectLifecycleReadonlyView({
      project_id: "P1",
      lifecycle_state: "stopped",
      closure_type: null,
      status_label: "Stopped",
      readonly: true,
      allowed_actions: ["resume", "close"],
      status: "cancelled",
      warnings: [],
    });

    expect(view.mode).toBe("stopped_readonly");
    expect(view.canResume).toBe(true);
    expect(view.canClose).toBe(true);
    expect(view.canWriteBusinessData).toBe(false);
    expect(view.message).toContain("paused");
  });

  it("marks completed close as archived readonly", () => {
    const view = deriveProjectLifecycleReadonlyView({
      project_id: "P1",
      lifecycle_state: "closed",
      closure_type: "completed",
      status_label: "Closed",
      readonly: true,
      allowed_actions: [],
      status: "closed",
      warnings: [],
    });

    expect(view.mode).toBe("closed_completed_readonly");
    expect(view.canResume).toBe(false);
    expect(view.canClose).toBe(false);
    expect(view.title).toBe("Project closed as completed");
  });

  it("marks administrative close as archived readonly", () => {
    const view = deriveProjectLifecycleReadonlyView({
      project_id: "P1",
      lifecycle_state: "closed",
      closure_type: "administrative",
      status_label: "Closed",
      readonly: true,
      allowed_actions: [],
      status: "closed",
      warnings: [],
    });

    expect(view.mode).toBe("closed_administrative_readonly");
    expect(view.canResume).toBe(false);
    expect(view.title).toBe("Project closed administratively");
  });

  it("maps TASK_338 readonly detail to business copy", () => {
    expect(
      deriveReadonlyApiErrorMessage({
        code: "project_lifecycle_readonly",
        project_id: "P1",
        lifecycle_state: "closed",
        closure_type: "administrative",
        message: "This project is closed administratively and is readonly.",
        allowed_actions: [],
      })
    ).toBe("This project is closed administratively and is read-only.");
  });
});
