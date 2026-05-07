import type { ChangeEvent, ReactElement, RefObject } from "react";

import type { IntakePackageImport } from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import type { IntakeSourceMode } from "./intakeSession";
import { mailDateText, senderEmailText } from "./intakeSelectors";

type IntakeSourcePanelProps = {
  directWordName: string | null;
  importError: string | null;
  importing: boolean;
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
  msgInputRef,
  onDirectWordChange,
  onMsgFileChange,
  onSelectSourceMode,
  packageImport,
  sourceMode,
  wordInputRef,
}: IntakeSourcePanelProps): ReactElement {
  return (
    <>
      <section className="intake-panel">
        <h3 className="ui-panel-title">Import source</h3>
        <div className="import-source-actions">
          <input
            ref={msgInputRef}
            accept=".msg"
            className="file-input-hidden"
            type="file"
            onChange={onMsgFileChange}
          />
          <input
            ref={wordInputRef}
            accept=".docx"
            className="file-input-hidden"
            type="file"
            onChange={onDirectWordChange}
          />
          <button
            className={sourceMode === "msg" ? "source-button source-button-active" : "source-button"}
            disabled={importing}
            type="button"
            onClick={() => {
              onSelectSourceMode("msg");
              msgInputRef.current?.click();
            }}
          >
            <UiIcon name="outlook" />
            {importing ? "Importing from Outlook..." : "Import from Outlook"}
          </button>
        </div>
        {importError ? <p className="intake-error">{importError}</p> : null}
      </section>

      <section className="intake-panel">
        <h3 className="ui-panel-title">Email information</h3>
        <dl className="email-info-list">
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
      </section>
    </>
  );
}
