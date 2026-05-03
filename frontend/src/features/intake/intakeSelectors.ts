import type { IntakeAsset, IntakeAssetPreview, IntakePackageImport } from "../../api/client";

export type IntakeAttachmentKind = "word" | "pdf" | "image" | "msg" | "file";

export type IntakeAttachmentViewModel = {
  asset: IntakeAsset;
  kind: IntakeAttachmentKind;
  label: string;
  roleText: string;
  selected: boolean;
  word: boolean;
};

export function visibleIntakeAttachments(packageImport: IntakePackageImport | null): IntakeAsset[] {
  return packageImport?.assets.filter((asset) => asset.asset_role !== "email_source") ?? [];
}

export function buildAttachmentViewModels(
  assets: IntakeAsset[],
  selectedAssetId: string | null,
): IntakeAttachmentViewModel[] {
  return assets.map((asset) => {
    const kind = assetKind(asset);
    return {
      asset,
      kind,
      label: assetKindLabelFromKind(kind, asset.extension),
      roleText: attachmentRoleText(asset),
      selected: asset.asset_id === selectedAssetId,
      word: isWordAsset(asset),
    };
  });
}

export function selectedIntakeAsset(
  packageImport: IntakePackageImport | null,
  selectedAssetId: string | null,
): IntakeAsset | null {
  return packageImport?.assets.find((asset) => asset.asset_id === selectedAssetId) ?? null;
}

export function selectedApplicationFormAsset(
  packageImport: IntakePackageImport | null,
  selectedWordAssetId: string | null,
): IntakeAsset | null {
  return packageImport?.assets.find((asset) => asset.asset_id === selectedWordAssetId) ?? null;
}

export function senderEmailText(item: IntakePackageImport | null): string {
  if (!item) {
    return "No email imported";
  }
  return item.sender_email || "No sender email";
}

export function mailDateText(item: IntakePackageImport | null): string {
  if (!item) {
    return "Waiting for source";
  }
  if (!item.received_at) {
    return "Direct upload";
  }
  const date = new Date(item.received_at);
  if (Number.isNaN(date.getTime())) {
    return item.received_at;
  }
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function isWordAsset(asset: IntakeAsset | null): boolean {
  if (!asset) {
    return false;
  }
  return [".doc", ".docx"].includes(asset.extension.toLowerCase());
}

export function assetKind(asset: IntakeAsset): IntakeAttachmentKind {
  const extension = asset.extension.toLowerCase();
  if (extension === ".doc" || extension === ".docx") {
    return "word";
  }
  if (extension === ".pdf") {
    return "pdf";
  }
  if ([".png", ".jpg", ".jpeg", ".tif", ".tiff"].includes(extension)) {
    return "image";
  }
  if (extension === ".msg") {
    return "msg";
  }
  return "file";
}

export function assetKindLabel(asset: IntakeAsset): string {
  return assetKindLabelFromKind(assetKind(asset), asset.extension);
}

export function assetKindFromPreview(preview: IntakeAssetPreview): IntakeAttachmentKind {
  return assetKind({
    asset_id: preview.metadata.asset_id,
    original_name: preview.metadata.original_name,
    extension: preview.metadata.extension,
    mime_type: preview.metadata.mime_type,
    size_bytes: preview.metadata.size_bytes,
    asset_role: preview.metadata.asset_role,
  });
}

export function assetKindLabelFromPreview(preview: IntakeAssetPreview): string {
  return assetKindLabelFromKind(assetKindFromPreview(preview), preview.metadata.extension);
}

export function assetTypeText(asset: IntakeAsset): string {
  if (isWordAsset(asset)) {
    return "Word Document";
  }
  if (asset.extension.toLowerCase() === ".pdf") {
    return "PDF Document";
  }
  return `${asset.extension.replace(".", "").toUpperCase()} Attachment`;
}

export function attachmentRoleText(asset: IntakeAsset): string {
  if (isWordAsset(asset)) {
    return "Application form candidate";
  }
  if (asset.asset_role && asset.asset_role !== "email_source") {
    return asset.asset_role.replaceAll("_", " ");
  }
  return "Supporting attachment";
}

export function previewStatusText(
  asset: IntakeAsset | null,
  preview: IntakeAssetPreview | null,
  loading: boolean,
  error: string | null,
): string {
  if (!asset) {
    return "Waiting";
  }
  if (loading) {
    return "Loading";
  }
  if (error) {
    return "Preview error";
  }
  if (preview?.kind === "docx_application_form") {
    return "Structured Word preview";
  }
  if (preview?.kind === "image") {
    return "Image preview";
  }
  if (preview?.kind === "metadata_only" || preview?.kind === "unsupported") {
    return "Metadata only";
  }
  return "Ready";
}

export function formatBytes(value: number): string {
  if (value >= 1024 * 1024) {
    return `${(value / 1024 / 1024).toFixed(1)} MB`;
  }
  if (value >= 1024) {
    return `${Math.round(value / 1024)} KB`;
  }
  return `${value} B`;
}

function assetKindLabelFromKind(kind: IntakeAttachmentKind, extension: string): string {
  if (kind === "word") {
    return "W";
  }
  if (kind === "pdf") {
    return "PDF";
  }
  if (kind === "image") {
    return "IMG";
  }
  if (kind === "msg") {
    return "MSG";
  }
  return extension.replace(".", "").toUpperCase() || "FILE";
}
