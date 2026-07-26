import type { ReactElement } from "react";

type Props = {
  disabledReason: string;
  busy: boolean;
  onExport: () => void;
};

export function MatrixEditorXlsxExportButton({
  disabledReason,
  busy,
  onExport,
}: Props): ReactElement {
  return (
    <button
      type="button"
      disabled={Boolean(disabledReason)}
      title={disabledReason || undefined}
      onClick={onExport}
    >
      {busy ? "Exporting..." : "导出 Matrix"}
    </button>
  );
}
