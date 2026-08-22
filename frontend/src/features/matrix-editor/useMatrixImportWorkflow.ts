import { useCallback, useRef, useState, type ChangeEvent } from "react";
import {
  commitMatrixImport,
  isProjectLifecycleReadonlyErrorDetail,
  isMatrixImportStandardVersionActionRequiredError,
  matrixPreviewPdfUrl,
  previewProjectTestPlanMatrixFromPath,
  previewProjectTestPlanMatrixFromSourceCandidate,
  previewProjectTestPlanMatrixFromUpload,
  type MatrixImportCommitResponse,
  type MatrixImportStandardVersionUnavailableAction,
  type MatrixPreviewResponse,
  type MatrixResolvedDirectoryCandidate,
} from "../../api/client";
import { hasMatrixImportSourcePicker } from "../../desktop/pathPickerBridge";
import {
  deriveReadonlyApiErrorMessage,
} from "../project-lifecycle/projectLifecycleReadonlyModel";
import { useMatrixImportSourcePicker } from "./useMatrixImportSourcePicker";
import { useMatrixImportStandardVersionChoice } from "./useMatrixImportStandardVersionChoice";

type ImportLocatorSnapshot = {
  page: string;
  tableOnPage: string;
  keyword: string;
};

type MatrixImportCommit = {
  preview: MatrixPreviewResponse;
  response: MatrixImportCommitResponse;
};

type UseMatrixImportWorkflowOptions = {
  projectId: string;
  readonlyMessage: string | null;
  onCommitted: (result: MatrixImportCommit) => void;
};

type MatrixImportSourcePickerView = {
  candidates: MatrixResolvedDirectoryCandidate[];
  close: () => void;
  error: string | null;
  loading: boolean;
  preview: (sourceAssetId: string) => Promise<void>;
  previewBusy: boolean;
  sourceTitle: string;
  uploadOtherFile: () => void;
};

export type MatrixImportDialogView = {
  actionBusy: boolean;
  close: () => void;
  error: string | null;
  fileName: string;
  importingPreview: boolean;
  locatorKeyword: string;
  locatorPage: string;
  locatorTableOnPage: string;
  lookupMessage: string;
  lookupTone: "success" | "error" | "idle";
  preview: MatrixPreviewResponse | null;
  previewPdfSrc: string | null;
  replace: () => Promise<void>;
  updateLocator: (next: Partial<ImportLocatorSnapshot>) => void;
};

function parseRequestError(error: unknown, fallback: string): string {
  const detail =
    error && typeof error === "object" && "detail" in error
      ? (error as { detail: unknown }).detail
      : null;
  if (isProjectLifecycleReadonlyErrorDetail(detail)) {
    return deriveReadonlyApiErrorMessage(detail);
  }
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }
  return fallback;
}

function parsePositiveInteger(input: string): number | null {
  const normalized = input.trim();
  if (!normalized) {
    return null;
  }
  const parsed = Number.parseInt(normalized, 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return null;
  }
  return parsed;
}

function previewImportLocatorSnapshot(preview: MatrixPreviewResponse): ImportLocatorSnapshot {
  return {
    page: preview.selected_page_number != null ? String(preview.selected_page_number) : "",
    tableOnPage:
      preview.selected_page_table_index != null ? String(preview.selected_page_table_index) : "",
    keyword: "",
  };
}

function importLocatorSnapshotsMatch(
  left: ImportLocatorSnapshot | null,
  right: ImportLocatorSnapshot | null,
): boolean {
  return Boolean(left && right) &&
    left?.page === right?.page &&
    left?.tableOnPage === right?.tableOnPage &&
    left?.keyword === right?.keyword;
}

export function useMatrixImportWorkflow({
  projectId,
  readonlyMessage,
  onCommitted,
}: UseMatrixImportWorkflowOptions) {
  const [preview, setPreview] = useState<MatrixPreviewResponse | null>(null);
  const [previewPdfToken, setPreviewPdfToken] = useState<string | null>(null);
  const [lastParsedLocator, setLastParsedLocator] = useState<ImportLocatorSnapshot | null>(null);
  const [importingPreview, setImportingPreview] = useState(false);
  const [openingPreview, setOpeningPreview] = useState(false);
  const [sourceCandidates, setSourceCandidates] =
    useState<MatrixResolvedDirectoryCandidate[] | null>(null);
  const [sourceCandidateTitle, setSourceCandidateTitle] = useState("Project source files");
  const [sourceCandidateLoading, setSourceCandidateLoading] = useState(false);
  const [sourceCandidateError, setSourceCandidateError] = useState<string | null>(null);
  const [sourceCandidatePreviewBusy, setSourceCandidatePreviewBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lookupMessage, setLookupMessage] = useState("");
  const [lookupTone, setLookupTone] = useState<"success" | "error" | "idle">("idle");
  const [commitMessage, setCommitMessage] = useState("");
  const [commitWarning, setCommitWarning] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [committing, setCommitting] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importSourcePath, setImportSourcePath] = useState<string | null>(null);
  const [committedSourceDocumentName, setCommittedSourceDocumentName] = useState<string | null>(null);
  const [locatorPage, setLocatorPage] = useState("");
  const [locatorTableOnPage, setLocatorTableOnPage] = useState("");
  const [locatorKeyword, setLocatorKeyword] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const sourcePickerRequestRef = useRef(0);
  const chooseMatrixImportSource = useMatrixImportSourcePicker(projectId);
  const standardVersionChoice = useMatrixImportStandardVersionChoice();

  const resetLookup = (): void => {
    setError(null);
    setCommitWarning("");
    setLookupMessage("");
    setLookupTone("idle");
  };

  const resetLocator = (): void => {
    setLocatorPage("");
    setLocatorTableOnPage("");
    setLocatorKeyword("");
    setLastParsedLocator(null);
  };

  const applyPreviewLocator = (nextPreview: MatrixPreviewResponse): void => {
    setLocatorPage(
      nextPreview.selected_page_number != null ? String(nextPreview.selected_page_number) : "",
    );
    setLocatorTableOnPage(
      nextPreview.selected_page_table_index != null
        ? String(nextPreview.selected_page_table_index)
        : "",
    );
    setLocatorKeyword("");
    setLastParsedLocator(previewImportLocatorSnapshot(nextPreview));
  };

  const applyPreviewStatus = (
    nextPreview: MatrixPreviewResponse,
    emptyGroupsMessage = "No matching matrix found. Adjust page/table, then Replace.",
  ): boolean => {
    if (nextPreview.blockers.length > 0) {
      setError(nextPreview.blockers[0]);
      setLookupMessage("No matching matrix found. Adjust page/table, then Replace.");
      setLookupTone("error");
      return false;
    }
    if (nextPreview.groups.length === 0) {
      setError("No matching matrix found.");
      setLookupMessage(emptyGroupsMessage);
      setLookupTone("error");
      return false;
    }
    setError(null);
    setLookupMessage(`Matrix found: ${nextPreview.groups.length} groups detected.`);
    setLookupTone("success");
    return true;
  };

  const resetSessionSource = useCallback((sessionPreview: MatrixPreviewResponse | null): void => {
    setPreview(sessionPreview);
    setCommittedSourceDocumentName(sessionPreview?.source_document_name?.trim() || null);
    setPreviewPdfToken(null);
    setImportFile(null);
    setDialogOpen(false);
    setError(null);
    setLookupMessage("");
    setLookupTone("idle");
  }, []);

  const openUploadPicker = (): void => {
    fileInputRef.current?.click();
  };

  const closeSourcePicker = (): void => {
    setSourceCandidates(null);
    setSourceCandidateTitle("Project source files");
    setSourceCandidateError(null);
  };

  const uploadOtherFile = (): void => {
    closeSourcePicker();
    openUploadPicker();
  };

  const openPreviewFromPath = async (sourcePath: string): Promise<void> => {
    setImportFile(null);
    setImportSourcePath(sourcePath);
    resetLocator();
    resetLookup();
    setPreview(null);
    setPreviewPdfToken(null);
    setImportingPreview(true);
    setOpeningPreview(true);
    try {
      const nextPreview = await previewProjectTestPlanMatrixFromPath({
        source_path: sourcePath,
        project_id: projectId,
      });
      setPreview(nextPreview);
      setPreviewPdfToken(nextPreview.preview_pdf_token ?? null);
      applyPreviewLocator(nextPreview);
      setDialogOpen(true);
      applyPreviewStatus(nextPreview);
    } catch (caught) {
      setError(parseRequestError(caught, "Failed to import Matrix."));
    } finally {
      setImportingPreview(false);
      setOpeningPreview(false);
    }
  };

  const previewSourceCandidate = async (sourceAssetId: string): Promise<void> => {
    if (readonlyMessage) {
      setError(readonlyMessage);
      return;
    }
    setSourceCandidatePreviewBusy(true);
    setOpeningPreview(true);
    setError(null);
    try {
      const nextPreview = await previewProjectTestPlanMatrixFromSourceCandidate(
        projectId,
        sourceAssetId,
        "resolved_directory",
      );
      closeSourcePicker();
      setImportFile(null);
      setImportSourcePath(null);
      applyPreviewLocator(nextPreview);
      setCommitWarning("");
      setLookupMessage("");
      setLookupTone("idle");
      setPreview(nextPreview);
      setPreviewPdfToken(nextPreview.preview_pdf_token ?? null);
      setDialogOpen(true);
      applyPreviewStatus(nextPreview);
    } catch (caught) {
      setSourceCandidateError(
        parseRequestError(caught, "Failed to preview the selected project source."),
      );
    } finally {
      setSourceCandidatePreviewBusy(false);
      setOpeningPreview(false);
    }
  };

  const chooseSource = async (): Promise<void> => {
    if (readonlyMessage) {
      setError(readonlyMessage);
      return;
    }
    const requestId = ++sourcePickerRequestRef.current;
    const usingBrowserPicker = !hasMatrixImportSourcePicker();
    if (usingBrowserPicker) {
      setSourceCandidates([]);
      setSourceCandidateTitle("Project source files");
      setSourceCandidateError(null);
      setSourceCandidateLoading(true);
    }
    const choice = await chooseMatrixImportSource();
    if (requestId !== sourcePickerRequestRef.current) {
      return;
    }
    setSourceCandidateLoading(false);
    if (choice.kind === "browser") {
      if (!Array.isArray(choice.candidates)) {
        closeSourcePicker();
        openUploadPicker();
        return;
      }
      setSourceCandidates(choice.candidates ?? []);
      setSourceCandidateTitle(choice.sourceTitle ?? "Project source files");
      setSourceCandidateError(choice.error ?? null);
      return;
    }
    if (choice.kind === "cancelled") {
      return;
    }
    if (choice.kind === "unsupported") {
      setError("Choose a PDF or Word document (.doc or .docx).");
      return;
    }
    await openPreviewFromPath(choice.path);
  };

  const currentLocatorSnapshot = (): ImportLocatorSnapshot => ({
    page: locatorPage.trim(),
    tableOnPage: locatorTableOnPage.trim(),
    keyword: locatorKeyword.trim(),
  });

  const parsedCurrentLocator = (
    preservePreviewOnError: boolean,
  ): {
    snapshot: ImportLocatorSnapshot;
    pageNumber: number | null;
    tableIndex: number | null;
  } | null => {
    const snapshot = currentLocatorSnapshot();
    const pageNumber = parsePositiveInteger(snapshot.page);
    const tableIndex = parsePositiveInteger(snapshot.tableOnPage);
    if (snapshot.page && pageNumber === null) {
      setError("Page must be a positive integer.");
      setLookupMessage("No matching matrix found. Adjust page/table, then Replace.");
      setLookupTone("error");
      if (!preservePreviewOnError) {
        setPreview(null);
      }
      return null;
    }
    if (snapshot.tableOnPage && tableIndex === null) {
      setError("Table on page must be a positive integer.");
      setLookupMessage("No matching matrix found. Adjust page/table, then Replace.");
      setLookupTone("error");
      if (!preservePreviewOnError) {
        setPreview(null);
      }
      return null;
    }
    return { snapshot, pageNumber, tableIndex };
  };

  const fetchPreviewForLocator = async (
    parsedLocator: {
      snapshot: ImportLocatorSnapshot;
      pageNumber: number | null;
      tableIndex: number | null;
    },
    preservePreviewOnNoMatch: boolean,
  ): Promise<MatrixPreviewResponse | null> => {
    if (!importFile && !importSourcePath) {
      return null;
    }
    const nextPreview = importFile
      ? await previewProjectTestPlanMatrixFromUpload(importFile, projectId, {
          pageNumber: parsedLocator.pageNumber,
          pageTableIndex: parsedLocator.tableIndex,
          tableTextQuery: parsedLocator.snapshot.keyword || null,
        })
      : await previewProjectTestPlanMatrixFromPath({
          source_path: importSourcePath as string,
          project_id: projectId,
          page_number: parsedLocator.pageNumber,
          page_table_index: parsedLocator.tableIndex,
          table_text_query: parsedLocator.snapshot.keyword || null,
        });
    if (nextPreview.preview_pdf_token) {
      setPreviewPdfToken(nextPreview.preview_pdf_token);
    }
    if (nextPreview.blockers.length > 0 || nextPreview.groups.length === 0) {
      if (!preservePreviewOnNoMatch) {
        setPreview(null);
      }
      applyPreviewStatus(nextPreview);
      return null;
    }
    const pageMismatch =
      parsedLocator.pageNumber != null &&
      nextPreview.selected_page_number !== parsedLocator.pageNumber;
    const tableMismatch =
      parsedLocator.tableIndex != null &&
      nextPreview.selected_page_table_index !== parsedLocator.tableIndex;
    if (pageMismatch || tableMismatch) {
      if (!preservePreviewOnNoMatch) {
        setPreview(null);
      }
      setError("Requested page/table did not match a matrix.");
      setLookupMessage(
        "No matching matrix found at requested page/table. Adjust the locator, then Replace.",
      );
      setLookupTone("error");
      return null;
    }
    return nextPreview;
  };

  const commitPreview = async (
    nextPreview: MatrixPreviewResponse,
    unavailableAction: MatrixImportStandardVersionUnavailableAction = "prompt_if_unavailable",
    allowUnavailableChoice = true,
  ): Promise<void> => {
    let response: MatrixImportCommitResponse;
    try {
      response = await commitMatrixImport(projectId, {
        source_document_path: nextPreview.source_document_path,
        source_document_name: nextPreview.source_document_name,
        source_format: nextPreview.source_format,
        preview_payload: nextPreview,
        selected_group_keys: nextPreview.groups.map((group) => group.group_key),
        standard_version_unavailable_action: unavailableAction,
      });
    } catch (caught) {
      if (
        allowUnavailableChoice &&
        isMatrixImportStandardVersionActionRequiredError(caught)
      ) {
        standardVersionChoice.open(caught.detail, (retryAction) =>
          commitPreview(nextPreview, retryAction, false),
        );
        setError(null);
        return;
      }
      throw caught;
    }

    onCommitted({ preview: nextPreview, response });
    setCommittedSourceDocumentName(nextPreview.source_document_name.trim() || null);
    const methodSummary = response.method_authority_sync;
    const updatedLabel = `${methodSummary.updated_count} Method${methodSummary.updated_count === 1 ? "" : "s"} updated`;
    const reviewLabel = `${methodSummary.review_count} row${methodSummary.review_count === 1 ? "" : "s"} need review`;
    if (methodSummary.warning) {
      setCommitMessage("");
      setCommitWarning(methodSummary.warning.message);
    } else {
      setCommitWarning("");
      setCommitMessage(
        `${response.commit_status === "reused" ? "Matrix import reused" : "Matrix replaced"}. ${updatedLabel}; ${reviewLabel}.`,
      );
    }
    setError(null);
    setDialogOpen(false);
  };

  const replace = async (): Promise<void> => {
    if (readonlyMessage) {
      setError(readonlyMessage);
      return;
    }
    if (!preview || preview.groups.length === 0) {
      setError("No valid matrix found from import.");
      return;
    }
    const previewStale = !importLocatorSnapshotsMatch(
      currentLocatorSnapshot(),
      lastParsedLocator,
    );
    setCommitting(true);
    try {
      if (previewStale) {
        const parsedLocator = parsedCurrentLocator(true);
        if (!parsedLocator) {
          return;
        }
        setImportingPreview(true);
        setError(null);
        setLookupMessage("");
        setLookupTone("idle");
        let refreshedPreview: MatrixPreviewResponse | null = null;
        try {
          refreshedPreview = await fetchPreviewForLocator(parsedLocator, true);
        } finally {
          setImportingPreview(false);
        }
        if (!refreshedPreview || !applyPreviewStatus(refreshedPreview)) {
          return;
        }
        setPreview(refreshedPreview);
        setLastParsedLocator(parsedLocator.snapshot);
        await commitPreview(refreshedPreview);
        return;
      }
      await commitPreview(preview);
    } catch (caught) {
      setError(parseRequestError(caught, "Failed to import Matrix."));
    } finally {
      setCommitting(false);
    }
  };

  const onFileChange = async (event: ChangeEvent<HTMLInputElement>): Promise<void> => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (readonlyMessage) {
      setError(readonlyMessage);
      return;
    }
    if (!file) {
      return;
    }
    sourcePickerRequestRef.current += 1;
    setSourceCandidateLoading(false);
    closeSourcePicker();
    setImportFile(file);
    setImportSourcePath(null);
    resetLocator();
    resetLookup();
    setPreview(null);
    setPreviewPdfToken(null);
    setImportingPreview(true);
    setOpeningPreview(true);
    try {
      const nextPreview = await previewProjectTestPlanMatrixFromUpload(file, projectId);
      setPreview(nextPreview);
      setPreviewPdfToken(nextPreview.preview_pdf_token ?? null);
      applyPreviewLocator(nextPreview);
      setDialogOpen(true);
      applyPreviewStatus(
        nextPreview,
        "No matching matrix found. Adjust the locator, then Replace.",
      );
    } catch (caught) {
      setPreview(null);
      setPreviewPdfToken(null);
      setLastParsedLocator(null);
      setError(caught instanceof Error ? caught.message : "Import preview failed.");
      setLookupMessage("No matching matrix found. Adjust page/table, then Replace.");
      setLookupTone("error");
      setDialogOpen(true);
    } finally {
      setImportingPreview(false);
      setOpeningPreview(false);
    }
  };

  const previewPageNumber = Number.parseInt(locatorPage.trim(), 10);
  const previewOpenPage =
    Number.isFinite(previewPageNumber) && previewPageNumber > 0 ? previewPageNumber : 1;
  const previewPdfSrc = previewPdfToken
    ? `${matrixPreviewPdfUrl(previewPdfToken)}#page=${previewOpenPage}&zoom=page-width&pagemode=thumbs`
    : null;
  const actionBusy = importingPreview || committing;
  const updateLocator = (next: Partial<ImportLocatorSnapshot>): void => {
    if (next.page !== undefined) {
      setLocatorPage(next.page);
    }
    if (next.tableOnPage !== undefined) {
      setLocatorTableOnPage(next.tableOnPage);
    }
    if (next.keyword !== undefined) {
      setLocatorKeyword(next.keyword);
    }
  };

  const sourcePicker: MatrixImportSourcePickerView | null = sourceCandidates
    ? {
        candidates: sourceCandidates,
        close: closeSourcePicker,
        error: sourceCandidateError,
        loading: sourceCandidateLoading,
        preview: previewSourceCandidate,
        previewBusy: sourceCandidatePreviewBusy,
        sourceTitle: sourceCandidateTitle,
        uploadOtherFile,
      }
    : null;

  const dialog: MatrixImportDialogView | null = dialogOpen
    ? {
        actionBusy,
        close: () => setDialogOpen(false),
        error,
        fileName:
          preview?.source_document_name ?? importFile?.name ?? importSourcePath ?? "Selected file",
        importingPreview,
        locatorKeyword,
        locatorPage,
        locatorTableOnPage,
        lookupMessage,
        lookupTone,
        preview,
        previewPdfSrc,
        replace,
        updateLocator,
      }
    : null;

  return {
    actionBusy,
    chooseSource,
    commitMessage,
    commitWarning,
    committedSourceDocumentName,
    dialog,
    fileInputRef,
    onFileChange,
    openingPreview,
    preview,
    resetSessionSource,
    sourcePicker,
    standardVersionChoice,
  };
}
