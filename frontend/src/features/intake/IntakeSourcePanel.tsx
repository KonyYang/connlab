import { useState, type ChangeEvent, type DragEvent, type ReactElement, type RefObject } from "react";

import type { IntakePackageImport } from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import type { IntakeSourceMode } from "./intakeSession";
import { mailDateText, senderEmailText } from "./intakeSelectors";

type IntakeSourcePanelProps = {
  directWordName: string | null;
  importError: string | null;
  importing: boolean;
  interactionLocked?: boolean;
  interactionLockedReason?: string;
  msgInputRef: RefObject<HTMLInputElement | null>;
  packageImport: IntakePackageImport | null;
  sourceMode: IntakeSourceMode;
  wordInputRef: RefObject<HTMLInputElement | null>;
  onDirectWordChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onMsgFileChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onSelectSourceMode: (mode: IntakeSourceMode) => void;
};

export function IntakeSourcePanel({
  directWordName,
  importError,
  importing,
  interactionLocked = false,
  interactionLockedReason = "Applying LTR number. Import is paused.",
  msgInputRef,
  onDirectWordChange,
  onMsgFileChange,
  onSelectSourceMode,
  packageImport,
  sourceMode,
  wordInputRef,
}: IntakeSourcePanelProps): ReactElement {
  const [isDragOver, setIsDragOver] = useState(false);
  const importDisabled = importing || interactionLocked;

  function handleDragOver(event: DragEvent<HTMLDivElement>): void {
    event.preventDefault();
    if (interactionLocked) {
      return;
    }
    setIsDragOver(true);
  }

  function handleDragLeave(event: DragEvent<HTMLDivElement>): void {
    event.preventDefault();
    setIsDragOver(false);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>): void {
    event.preventDefault();
    setIsDragOver(false);
    if (interactionLocked) {
      return;
    }
    const file = event.dataTransfer.files[0];
    if (!file || !file.name.toLowerCase().endsWith(".msg")) {
      return;
    }
    onSelectSourceMode("msg");
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    const syntheticEvent = {
      target: {
        files: dataTransfer.files,
        value: "",
      } as HTMLInputElement,
    } as ChangeEvent<HTMLInputElement>;
    onMsgFileChange(syntheticEvent);
  }

  const hasPackage = packageImport !== null;

  return (
    <section className="intake-panel email-source-panel">
      <div className="email-source-header">
        <h3 className="ui-panel-title">Email source</h3>
        <input
          ref={msgInputRef}
          accept=".msg"
          className="file-input-hidden"
          disabled={importDisabled}
          type="file"
          onChange={onMsgFileChange}
        />
        <input
          ref={wordInputRef}
          accept=".docx"
          className="file-input-hidden"
          disabled={importDisabled}
          type="file"
          onChange={onDirectWordChange}
        />
        <button
          className={sourceMode === "msg" ? "source-button source-button-active" : "source-button"}
          disabled={importDisabled}
          title={interactionLocked ? interactionLockedReason : undefined}
          type="button"
          onClick={() => {
            if (importDisabled) {
              return;
            }
            onSelectSourceMode("msg");
            msgInputRef.current?.click();
          }}
        >
          <UiIcon name="outlook" />
          Import
        </button>
      </div>

      <div
        className={"email-drop-zone"
          + (isDragOver ? " email-drop-zone-active" : "")
          + (hasPackage ? " email-drop-zone-filled" : "")
          + (interactionLocked ? " email-drop-zone-locked" : "")}
        aria-disabled={interactionLocked ? true : undefined}
        title={interactionLocked ? interactionLockedReason : undefined}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {!hasPackage ? (
          <div className="email-drop-zone-prompt">
            <UiIcon name="upload" />
            <span>Drop a .msg email file here</span>
          </div>
        ) : (
          <dl className="email-info-list">
            <div>
              <dt>Source file</dt>
              <dd className="email-source-filename" title={packageImport?.source_original_name ?? ""}>
                {packageImport?.source_original_name || "No source file"}
              </dd>
            </div>
            <div>
              <dt>From</dt>
              <dd>{senderEmailText(packageImport)}</dd>
            </div>
            <div>
              <dt>Subject</dt>
              <dd>{packageImport?.subject || directWordName || "No subject"}</dd>
            </div>
            <div>
              <dt>Date</dt>
              <dd>{mailDateText(packageImport)}</dd>
            </div>
          </dl>
        )}
      </div>

      {importError ? <p className="intake-error">{importError}</p> : null}
    </section>
  );
}
