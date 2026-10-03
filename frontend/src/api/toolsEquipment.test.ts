import { afterEach, expect, it, vi } from "vitest";
import { updateStandaloneEquipmentList } from "./client";

afterEach(() => vi.unstubAllGlobals());

it("transports report and equipment uploads and reads download review metadata", async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response("updated", { headers: {
    "Content-Disposition": "attachment; filename*=UTF-8''Internal_EquipmentUpdated.docx",
    "X-Equipment-Review": JSON.stringify({ filled: 1, unmatched: [], incomplete: [], expired: [],
      omitted: { unmatched: 0, incomplete: 0, expired: 0 } }),
  } }));
  vi.stubGlobal("fetch", fetchMock);
  const report = new File(["source"], "Internal.docx");
  const equipment = new File(["IDs"], "EquipmentID.docx");
  const response = await updateStandaloneEquipmentList(report, { equipmentFile: equipment });
  expect(response.fileName).toBe("Internal_EquipmentUpdated.docx");
  expect(response.blob.size).toBe(7);
  expect(response.review.filled).toBe(1);
  const body = fetchMock.mock.calls[0][1].body as FormData;
  expect((body.get("file") as File).name).toBe("Internal.docx");
  expect((body.get("equipment_file") as File).name).toBe("EquipmentID.docx");
  expect(body.has("references_text")).toBe(false);
});

it("surfaces server guidance instead of downloading an error response", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Check Settings." }), {
    status: 422, headers: { "Content-Type": "application/json" },
  })));
  await expect(updateStandaloneEquipmentList(new File(["report"], "report.docx"), {
    referencesText: "Q-0033",
  })).rejects.toThrow("Check Settings.");
});

it.each(["null", "invalid JSON", '{"filled":1}'])("handles invalid feedback %s without crashing Tools", async (header) => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("copy", { headers: {
    "X-Equipment-Review": header,
  } })));
  await expect(updateStandaloneEquipmentList(new File(["report"], "report.docx"), {
    referencesText: "Q-0033",
  })).rejects.toThrow("Equipment update feedback is unavailable. Retry the update.");
});
