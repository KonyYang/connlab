import { afterEach, expect, it, vi } from "vitest";
import { encryptStandaloneFolder, encryptLocalFolder } from "./client";

afterEach(() => vi.unstubAllGlobals());

it("starts native local-folder processing with no file body", async () => {
  const value = { cancelled: true };
  const mock = vi.fn().mockResolvedValue(new Response(JSON.stringify(value)));
  vi.stubGlobal("fetch", mock);
  expect(await encryptLocalFolder()).toEqual(value);
  expect(mock.mock.calls[0][0]).toContain("/api/tools/encrypt-local-folder");
  expect(mock.mock.calls[0][1].body).toBeUndefined();
  expect(mock.mock.calls[0][1].headers).toMatchObject({ "X-ConnLab-Local-Encryption": "1" });
});

it("uploads files with recursive relative paths and reads the ZIP outcome counts", async () => {
  const mock = vi.fn().mockResolvedValue(new Response("zip", { headers: {
    "Content-Disposition": "attachment; filename=Encrypted_Folder.zip",
    "X-Encryption-Summary": '{"succeeded":0,"failed":1,"skipped":0}',
  } }));
  vi.stubGlobal("fetch", mock);
  const file = new File(["original"], "DL-2026-10-001.xlsx");
  Object.defineProperty(file, "webkitRelativePath", { value: "项目/子目录/DL-2026-10-001.xlsx" });
  const response = await encryptStandaloneFolder([file]);
  expect(response.fileName).toBe("Encrypted_Folder.zip");
  expect(response.summary.failed).toBe(1);
  const body = mock.mock.calls[0][1].body as FormData;
  expect(JSON.parse(body.get("relative_paths") as string)).toEqual(["项目/子目录/DL-2026-10-001.xlsx"]);
  expect((body.getAll("files")[0] as File).name).toBe(file.name);
});

it.each(["null", "invalid", '{"succeeded":1,"failed":-1,"skipped":0}', '{"succeeded":2,"failed":0,"skipped":0}'])(
  "does not download when batch verification metadata is invalid: %s", async header => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("not verified", { headers: { "X-Encryption-Summary": header } })));
    await expect(encryptStandaloneFolder([new File(["original"], "report.docx")])).rejects.toThrow("feedback is unavailable");
  });

it("surfaces server validation instead of treating it as a ZIP", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Select one folder at a time." }), {
    status: 422, headers: { "Content-Type": "application/json" },
  })));
  await expect(encryptStandaloneFolder([])).rejects.toThrow("Select one folder at a time");
});
