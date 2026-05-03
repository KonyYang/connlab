import { useEffect, useMemo, useRef, useState, type ChangeEvent, type ReactElement } from "react";
import {
  getIntakeAssetPreview,
  importDirectWordApplicationForm,
  importMsgPackage,
  selectIntakeApplicationForm,
  type IntakeAssetPreview,
  type IntakePackageImport
} from "../api/client";
import { NewProjectWorkflowHeader } from "../components/workflow/NewProjectWorkflow";
import { AttachmentList } from "../features/intake/AttachmentList";
import { AttachmentPreviewPanel } from "../features/intake/AttachmentPreviewPanel";
import { IntakeSourcePanel } from "../features/intake/IntakeSourcePanel";
import {
  EMPTY_INTAKE_SESSION,
  type IntakeSessionState
} from "../features/intake/intakeSession";
import {
  buildAttachmentViewModels,
  isWordAsset,
  selectedApplicationFormAsset,
  selectedIntakeAsset,
  visibleIntakeAttachments
} from "../features/intake/intakeSelectors";
import "../intake-inbox.css";

type IntakeInboxPageProps = {
  session: IntakeSessionState;
  onSessionChange: (session: IntakeSessionState) => void;
  onOpenPackage: (packageId: string, caseId?: string | null) => void;
};

export function IntakeInboxPage({
  session,
  onSessionChange,
  onOpenPackage
}: IntakeInboxPageProps): ReactElement {
  const msgInputRef = useRef<HTMLInputElement | null>(null);
  const wordInputRef = useRef<HTMLInputElement | null>(null);
  const [importing, setImporting] = useState(false);
  const [preparingPrecheck, setPreparingPrecheck] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [preview, setPreview] = useState<IntakeAssetPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const { packageImport, selectedAssetId, selectedWordAssetId, sourceMode, directWordName } = session;

  const selectedAsset = useMemo(
    () => selectedIntakeAsset(packageImport, selectedAssetId),
    [packageImport, selectedAssetId]
  );
  const selectedApplicationForm = useMemo(
    () => selectedApplicationFormAsset(packageImport, selectedWordAssetId),
    [packageImport, selectedWordAssetId]
  );
  const visibleAttachmentAssets = useMemo(
    () => visibleIntakeAttachments(packageImport),
    [packageImport]
  );
  const attachmentViewModels = useMemo(
    () => buildAttachmentViewModels(visibleAttachmentAssets, selectedAssetId),
    [selectedAssetId, visibleAttachmentAssets]
  );

  useEffect(() => {
    if (!selectedAssetId) {
      setPreview(null);
      setPreviewError(null);
      setPreviewLoading(false);
      return;
    }
    let cancelled = false;
    setPreviewLoading(true);
    setPreviewError(null);
    getIntakeAssetPreview(selectedAssetId)
      .then((result) => {
        if (!cancelled) {
          setPreview(result);
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setPreview(null);
          setPreviewError(error instanceof Error ? error.message : "Attachment preview failed.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setPreviewLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [selectedAssetId]);

  async function handleMsgFileChange(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    setImporting(true);
    setImportError(null);
    try {
      const imported = await importMsgPackage(file);
      const firstWord = imported.assets.find(isWordAsset) ?? null;
      onSessionChange({
        packageImport: imported,
        selectedAssetId: firstWord?.asset_id ?? imported.assets[0]?.asset_id ?? null,
        selectedWordAssetId: firstWord?.asset_id ?? null,
        selectedPrecheckCaseId: null,
        sourceMode: "msg",
        directWordName: null
      });
    } catch (error) {
      onSessionChange(EMPTY_INTAKE_SESSION);
      setImportError(error instanceof Error ? error.message : "Import failed.");
    } finally {
      setImporting(false);
    }
  }

  async function handleDirectWordChange(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    setImporting(true);
    setImportError(null);
    try {
      const imported = await importDirectWordApplicationForm(file);
      const firstWord = imported.assets.find(isWordAsset) ?? imported.assets[0] ?? null;
      onSessionChange({
        packageImport: imported,
        selectedAssetId: firstWord?.asset_id ?? null,
        selectedWordAssetId: firstWord?.asset_id ?? null,
        selectedPrecheckCaseId: null,
        sourceMode: "word",
        directWordName: file.name
      });
    } catch (error) {
      onSessionChange(EMPTY_INTAKE_SESSION);
      setImportError(error instanceof Error ? error.message : "Direct application form import failed.");
    } finally {
      setImporting(false);
    }
  }

  async function handleContinueToPrecheck(): Promise<void> {
    if (!packageImport || !selectedApplicationForm) {
      return;
    }
    setPreparingPrecheck(true);
    setImportError(null);
    try {
      const selection = await selectIntakeApplicationForm(
        packageImport.package_id,
        selectedApplicationForm.asset_id
      );
      onSessionChange({
        ...session,
        selectedPrecheckCaseId: selection.case_id,
        selectedWordAssetId: selection.selected_form_asset_id,
        selectedAssetId: selection.selected_form_asset_id
      });
      onOpenPackage(packageImport.package_id, selection.case_id);
    } catch (error) {
      setImportError(error instanceof Error ? error.message : "Unable to prepare Precheck review case.");
    } finally {
      setPreparingPrecheck(false);
    }
  }

  return (
    <section className="intake-workflow">
      <NewProjectWorkflowHeader currentStep="intake" />

      <div className="intake-step-grid">
        <aside className="intake-left-stack">
          <IntakeSourcePanel
            directWordName={directWordName}
            importError={importError}
            importing={importing}
            msgInputRef={msgInputRef}
            packageImport={packageImport}
            sourceMode={sourceMode}
            wordInputRef={wordInputRef}
            onDirectWordChange={(event) => void handleDirectWordChange(event)}
            onMsgFileChange={(event) => void handleMsgFileChange(event)}
          />
          <AttachmentList
            attachments={attachmentViewModels}
            packageLoaded={Boolean(packageImport)}
            onSelect={(attachment) => {
              onSessionChange({
                ...session,
                selectedAssetId: attachment.asset.asset_id,
                selectedWordAssetId: attachment.word ? attachment.asset.asset_id : selectedWordAssetId,
                selectedPrecheckCaseId: attachment.word ? null : session.selectedPrecheckCaseId
              });
            }}
          />
        </aside>

        <AttachmentPreviewPanel
          directWordName={directWordName}
          error={previewError}
          loading={previewLoading}
          preview={preview}
          selectedAsset={selectedAsset}
        />
      </div>

      <div className="step-footer">
        <span className="step-footer-guidance">
          {selectedApplicationForm
            ? `Application form: ${selectedApplicationForm.original_name}`
            : "Select a Word (.docx) file before continuing."}
        </span>
        <button
          className="new-project-primary-action continue-action"
          disabled={!packageImport || !selectedApplicationForm || preparingPrecheck}
          type="button"
          onClick={() => void handleContinueToPrecheck()}
        >
          {preparingPrecheck ? "Preparing Precheck..." : "Continue to Precheck"}
          <span aria-hidden="true">&gt;</span>
        </button>
      </div>
    </section>
  );
}
