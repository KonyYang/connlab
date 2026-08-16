#!/usr/bin/env node
import fs from "node:fs";

function fail(message) {
  throw new Error(message);
}

function parseArgs(argv) {
  const result = { validateOnly: false, config: null };
  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];
    if (item === "--validate-only") result.validateOnly = true;
    else if (item === "--config") result.config = argv[++index];
    else fail(`Unknown argument: ${item}`);
  }
  if (!result.config) fail("--config is required.");
  return result;
}

export function validateConfig(value) {
  const keys = new Set([
    "schema", "version", "endpoint", "url", "viewports", "required_selectors",
    "required_text", "forbidden_console_patterns", "timeout_ms",
  ]);
  if (!value || typeof value !== "object" || Array.isArray(value) || Object.keys(value).some((key) => !keys.has(key)) || Object.keys(value).length !== keys.size) {
    fail("UI smoke config keys are invalid.");
  }
  if (value.schema !== "connlab.ui-smoke" || value.version !== 1) fail("UI smoke config identity is invalid.");
  for (const field of ["endpoint", "url"]) {
    if (typeof value[field] !== "string" || !/^https?:\/\//.test(value[field])) fail(`${field} must be an HTTP(S) URL.`);
  }
  if (!Array.isArray(value.viewports) || value.viewports.length === 0) fail("At least one viewport is required.");
  const names = new Set();
  for (const viewport of value.viewports) {
    if (!viewport || Object.keys(viewport).sort().join(",") !== "height,name,width" || typeof viewport.name !== "string" || !viewport.name || !Number.isInteger(viewport.width) || !Number.isInteger(viewport.height) || viewport.width < 320 || viewport.height < 320 || names.has(viewport.name)) {
      fail("Viewport identity or dimensions are invalid.");
    }
    names.add(viewport.name);
  }
  for (const field of ["required_selectors", "required_text", "forbidden_console_patterns"]) {
    if (!Array.isArray(value[field]) || value[field].some((item) => typeof item !== "string" || !item)) fail(`${field} must be a string array.`);
  }
  if (!Number.isInteger(value.timeout_ms) || value.timeout_ms < 1000 || value.timeout_ms > 120000) fail("timeout_ms is invalid.");
  return value;
}

class CdpClient {
  constructor(url, timeoutMs) {
    this.ws = new WebSocket(url);
    this.timeoutMs = timeoutMs;
    this.sequence = 0;
    this.pending = new Map();
    this.listeners = new Map();
  }

  async open() {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("CDP WebSocket open timed out.")), this.timeoutMs);
      this.ws.addEventListener("open", () => { clearTimeout(timer); resolve(); }, { once: true });
      this.ws.addEventListener("error", () => { clearTimeout(timer); reject(new Error("CDP WebSocket failed.")); }, { once: true });
    });
    this.ws.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (message.id && this.pending.has(message.id)) {
        const { resolve, reject, timer } = this.pending.get(message.id);
        clearTimeout(timer);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(message.error.message)); else resolve(message.result ?? {});
      } else if (message.method) {
        for (const listener of this.listeners.get(message.method) ?? []) listener(message.params ?? {});
      }
    });
  }

  send(method, params = {}) {
    const id = ++this.sequence;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`${method} timed out.`)); }, this.timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  once(method) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error(`${method} timed out.`)), this.timeoutMs);
      const listener = (params) => {
        clearTimeout(timer);
        this.listeners.set(method, (this.listeners.get(method) ?? []).filter((item) => item !== listener));
        resolve(params);
      };
      this.listeners.set(method, [...(this.listeners.get(method) ?? []), listener]);
    });
  }

  on(method, listener) {
    this.listeners.set(method, [...(this.listeners.get(method) ?? []), listener]);
  }

  close() { this.ws.close(); }
}

async function run(config) {
  const endpoint = config.endpoint.replace(/\/$/, "");
  const created = await fetch(`${endpoint}/json/new?${encodeURIComponent("about:blank")}`, { method: "PUT" });
  if (!created.ok) fail(`Cannot create CDP page: ${created.status}.`);
  const target = await created.json();
  if (!target.id || !target.webSocketDebuggerUrl) fail("CDP page identity is incomplete.");
  const client = new CdpClient(target.webSocketDebuggerUrl, config.timeout_ms);
  const consoleEntries = [];
  const exceptions = [];
  try {
    await client.open();
    client.on("Runtime.consoleAPICalled", (event) => consoleEntries.push((event.args ?? []).map((item) => item.value ?? item.description ?? "").join(" ")));
    client.on("Runtime.exceptionThrown", (event) => exceptions.push(event.exceptionDetails?.text ?? "runtime exception"));
    await Promise.all([client.send("Page.enable"), client.send("Runtime.enable")]);
    const results = [];
    for (const viewport of config.viewports) {
      await client.send("Emulation.setDeviceMetricsOverride", { width: viewport.width, height: viewport.height, deviceScaleFactor: 1, mobile: false });
      const loaded = client.once("Page.loadEventFired");
      await client.send("Page.navigate", { url: config.url });
      await loaded;
      const expression = `(() => {
        const selectors = ${JSON.stringify(config.required_selectors)};
        const texts = ${JSON.stringify(config.required_text)};
        const bodyText = document.body?.innerText ?? "";
        return {
          missing_selectors: selectors.filter((value) => !document.querySelector(value)),
          missing_text: texts.filter((value) => !bodyText.includes(value)),
          horizontal_overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
          ready_state: document.readyState,
        };
      })()`;
      const evaluated = await client.send("Runtime.evaluate", { expression, returnByValue: true });
      results.push({ viewport, ...evaluated.result.value });
    }
    const forbidden = consoleEntries.filter((entry) => config.forbidden_console_patterns.some((pattern) => new RegExp(pattern, "i").test(entry)));
    const passed = results.every((item) => item.missing_selectors.length === 0 && item.missing_text.length === 0 && !item.horizontal_overflow && item.ready_state === "complete") && exceptions.length === 0 && forbidden.length === 0;
    return { schema: "connlab.ui-smoke-result", version: 1, status: passed ? "passed" : "failed", url: config.url, viewports: results, exceptions, forbidden_console: forbidden };
  } finally {
    client.close();
    await fetch(`${endpoint}/json/close/${encodeURIComponent(target.id)}`).catch(() => undefined);
  }
}

async function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    const config = validateConfig(JSON.parse(fs.readFileSync(args.config, "utf8")));
    const result = args.validateOnly
      ? { schema: "connlab.ui-smoke-result", version: 1, status: "valid" }
      : await run(config);
    process.stdout.write(`${JSON.stringify(result)}\n`);
    process.exitCode = ["valid", "passed"].includes(result.status) ? 0 : 1;
  } catch (error) {
    process.stdout.write(`${JSON.stringify({ schema: "connlab.ui-smoke-result", version: 1, status: "blocked", reason: error.message })}\n`);
    process.exitCode = 2;
  }
}

await main();
