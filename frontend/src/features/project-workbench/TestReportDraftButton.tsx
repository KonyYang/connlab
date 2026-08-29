import type { ReactElement } from "react";

type TestReportDraftButtonProps = {
  onOpen: () => void;
};

export function TestReportDraftButton({
  onOpen,
}: TestReportDraftButtonProps): ReactElement {
  return (
    <div className="runtime-console-test-report-action">
      <button
        onClick={onOpen}
        title="Open Report Workspace"
        type="button"
      >
        Test Report
      </button>
    </div>
  );
}
