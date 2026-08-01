import { useEffect, useRef, type ReactElement } from "react";

type MatrixImportStandardVersionChoiceDialogProps = {
  open: boolean;
  busy: boolean;
  error: string | null;
  onChooseFile: () => void;
  onSkip: () => void;
  onClose: () => void;
};

export function MatrixImportStandardVersionChoiceDialog({
  open,
  busy,
  error,
  onChooseFile,
  onSkip,
  onClose,
}: MatrixImportStandardVersionChoiceDialogProps): ReactElement | null {
  const chooseButtonRef = useRef<HTMLButtonElement>(null);
  const returnFocusRef = useRef<HTMLElement | null>(null);
  const busyRef = useRef(busy);
  const onCloseRef = useRef(onClose);

  useEffect(() => {
    busyRef.current = busy;
    onCloseRef.current = onClose;
  }, [busy, onClose]);

  useEffect(() => {
    if (!open) {
      return undefined;
    }
    returnFocusRef.current = document.activeElement as HTMLElement | null;
    chooseButtonRef.current?.focus();

    function onKeyDown(event: KeyboardEvent): void {
      if (event.key === "Escape" && !busyRef.current) {
        event.preventDefault();
        onCloseRef.current();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      returnFocusRef.current?.focus();
      returnFocusRef.current = null;
    };
  }, [open]);

  if (!open) {
    return null;
  }

  return (
    <section className="matrix-import-standard-choice-backdrop">
      <article
        aria-describedby="matrix-import-standard-choice-description"
        aria-labelledby="matrix-import-standard-choice-title"
        aria-modal="true"
        className="matrix-import-standard-choice-dialog"
        role="dialog"
      >
        <h3 id="matrix-import-standard-choice-title">Standard version file unavailable</h3>
        <p id="matrix-import-standard-choice-description">
          Choose a Standard version file, or skip for now and keep the original Method values.
        </p>
        {error ? (
          <p aria-live="polite" className="matrix-import-standard-choice-error" role="status">
            {error}
          </p>
        ) : null}
        <footer>
          <button
            className="matrix-editor-import-secondary-button"
            disabled={busy}
            onClick={onSkip}
            type="button"
          >
            Skip for now
          </button>
          <button
            className="matrix-editor-import-commit-button"
            disabled={busy}
            onClick={onChooseFile}
            ref={chooseButtonRef}
            type="button"
          >
            Choose file
          </button>
        </footer>
      </article>
    </section>
  );
}
