import { useState, type ReactElement } from "react";
import { generateConfirmedMatrixTestRecordDraft } from "../../api/client";

type TestRecordDraftGenerationButtonProps = {
  projectId: string;
  ready: boolean;
};

export function TestRecordDraftGenerationButton({
  projectId,
  ready,
}: TestRecordDraftGenerationButtonProps): ReactElement {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate(): Promise<void> {
    if (!ready || generating) {
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      const blob = await generateConfirmedMatrixTestRecordDraft(projectId);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${projectId}_test_record_draft.docx`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch {
      setError("Unable to generate Test Record draft. Confirm Matrix authority and try again.");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="runtime-console-test-record-generation">
      <button
        disabled={!ready || generating}
        onClick={() => void handleGenerate()}
        type="button"
      >
        {generating ? "Generating..." : "Generate Test Record Draft"}
      </button>
      {!ready ? (
        <p>Confirm Matrix authority before generating a Test Record draft.</p>
      ) : null}
      {error ? <p className="error">{error}</p> : null}
    </div>
  );
}
