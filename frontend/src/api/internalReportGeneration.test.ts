import {afterEach, expect, it, vi} from "vitest";
import {downloadInternalReportDraft} from "./client";

afterEach(() => vi.unstubAllGlobals());

it("downloads the preview-bound draft using the server filename", async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response("draft bytes", {headers: {
    "Content-Disposition": "attachment; filename*=UTF-8''Internal%20Report_Draft.docx",
  }}));
  vi.stubGlobal("fetch", fetchMock);
  const result = await downloadInternalReportDraft("project/1", "a".repeat(64));
  expect(result.fileName).toBe("Internal Report_Draft.docx");
  expect(result.blob.size).toBe(11);
  expect(fetchMock.mock.calls[0][0]).toBe("/api/projects/project%2F1/report-workspace/internal-report/download-draft");
  expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({preview_token: "a".repeat(64)});
});

it("surfaces a changed preview instead of downloading an error", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({detail: "Preview generation again."}), {
    status: 409, headers: {"Content-Type": "application/json"},
  })));
  await expect(downloadInternalReportDraft("project-1", "a".repeat(64))).rejects.toThrow("Preview generation again.");
});
