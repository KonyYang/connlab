import { useState, type ReactElement } from "react";
import { generateTestReportDraftDownload } from "../../api/client";

type TestReportDraftButtonProps = {
  projectId: string;
  ready: boolean;
};

const NOT_READY_TITLE =
  "Confirm Basic Information and publish an Active Confirmed Matrix before generating a Test Report.";

export function TestReportDraftButton({
  projectId,
  ready,
}: TestReportDraftButtonProps): ReactElement {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate(): Promise<void> {
    if (!ready || generating) {
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      const download = await generateTestReportDraftDownload(projectId);
      const url = URL.createObjectURL(download.blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download =
        download.fileName ?? `${projectId} Test Report_Rev_A_Draft.docx`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate the Test Report draft."
      );
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="runtime-console-test-report-action">
      <button
        disabled={!ready || generating}
        onClick={() => void handleGenerate()}
        title={!ready ? NOT_READY_TITLE : "Generate and download an E-3707_H draft"}
        type="button"
      >
        {generating ? "Generating report..." : "Test Report"}
      </button>
      {error ? (
        <span className="runtime-console-command-error" role="alert">
          {error}
        </span>
      ) : null}
    </div>
  );
}
