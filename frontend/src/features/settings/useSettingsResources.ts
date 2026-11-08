import { useEffect, useRef, useState } from "react";
import { listExternalResources, saveExternalResource, validateExternalResource, type ExternalResource, type ExternalResourceType } from "../../api/client";

import { SHARED_RESOURCE_CONFIGS } from "./settingsResourceConfig";

const displayedTypes = new Set(SHARED_RESOURCE_CONFIGS.map(row => row.resourceType));
type SaveInput = {path: string; active: boolean; worksheet_name?: string | null};
type Messages = Partial<Record<ExternalResourceType, string | null>>;
function message(reason: string | null): string {
  if (reason?.startsWith("Expected an existing file:")) return "File does not exist.";
  if (reason?.startsWith("Expected an existing directory:")) return "Folder does not exist.";
  return reason ?? "Invalid path";
}
function sameConfiguration(a: ExternalResource, b?: ExternalResource): boolean {
  return !!b && a.resource_type === b.resource_type && a.resource_id === b.resource_id && a.path === b.path && a.active === b.active && a.worksheet_name === b.worksheet_name;
}

export function useSettingsResources() {
  const [resources, setResources] = useState<ExternalResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingType, setSavingType] = useState<ExternalResourceType | null>(null);
  const [pathValidationMessages, setMessages] = useState<Messages>({});
  const current = useRef<ExternalResource[]>([]);
  const live = useRef(false);
  const versions = useRef<Partial<Record<ExternalResourceType, number>>>({});
  const dirty = useRef(new Set<ExternalResourceType>());
  const pendingSaves = useRef(new Map<ExternalResourceType, number>());
  const tail = useRef(Promise.resolve());
  const refreshing = useRef(false);
  const refreshAgain = useRef(false);
  const focusTimer = useRef<number | undefined>(undefined);

  function enqueue<T>(job: () => Promise<T>): Promise<T> {
    const next = tail.current.then(job);
    tail.current = next.then(() => undefined, () => undefined);
    return next;
  }
  function upsert(resource: ExternalResource) {
    current.current = [...current.current.filter(row => row.resource_type !== resource.resource_type), resource];
    setResources(current.current);
  }
  function isCurrent(resource: ExternalResource, version: number) {
    const type = resource.resource_type;
    return live.current && (versions.current[type] ?? 0) === version && !dirty.current.has(type)
      && sameConfiguration(resource, current.current.find(row => row.resource_type === type));
  }
  async function check(resource: ExternalResource, version: number) {
    if (!isCurrent(resource, version)) return;
    try {
      const validated = await validateExternalResource(resource.resource_type);
      if (!isCurrent(resource, version) || !sameConfiguration(resource, validated)) return;
      upsert(validated);
      setMessages(previous => ({...previous, [resource.resource_type]: validated.validation_status === "invalid" ? message(validated.validation_failure_reason) : null}));
    } catch (cause) {
      if (isCurrent(resource, version)) setMessages(previous => ({...previous, [resource.resource_type]: (cause as Error).message}));
    }
  }
  function scheduleRefresh() {
    if (document.visibilityState === "hidden") return;
    window.clearTimeout(focusTimer.current);
    focusTimer.current = window.setTimeout(() => {void refresh();}, 250);
  }
  async function refresh() {
    if (!live.current) return;
    if (refreshing.current) {refreshAgain.current = true; return;}
    refreshing.current = true;
    try {
      const loaded = await enqueue(() => live.current ? listExternalResources() : Promise.resolve([]));
      if (!live.current) return;
      current.current = loaded;
      setResources(loaded);
      setError(null);
      setLoading(false);
      setMessages(previous => {
        const next = {...previous};
        for (const row of loaded) if (!dirty.current.has(row.resource_type) && !pendingSaves.current.has(row.resource_type)) {
          next[row.resource_type] = row.validation_status === "invalid" ? message(row.validation_failure_reason) : null;
        }
        return next;
      });
      // Queue each probe separately so an operator save can run before the next Office check.
      const probes = [...loaded].sort((a, b) => {
        const isFolder = (type: ExternalResourceType) => SHARED_RESOURCE_CONFIGS.find(row => row.resourceType === type)?.expectedKind === "Folder";
        return Number(isFolder(b.resource_type)) - Number(isFolder(a.resource_type));
      });
      for (const row of probes) {
        if (!live.current) break;
        if (!displayedTypes.has(row.resource_type) || !row.active || !row.path.trim() || dirty.current.has(row.resource_type) || pendingSaves.current.has(row.resource_type)) continue;
        const version = versions.current[row.resource_type] ?? 0;
        await enqueue(() => pendingSaves.current.has(row.resource_type) ? Promise.resolve() : check(row, version));
      }
    } catch (cause) {
      if (live.current) setError((cause as Error).message);
    } finally {
      refreshing.current = false;
      if (live.current) {
        setLoading(false);
        if (refreshAgain.current) {refreshAgain.current = false; scheduleRefresh();}
      }
    }
  }
  useEffect(() => {
    live.current = true;
    void refresh();
    window.addEventListener("focus", scheduleRefresh);
    document.addEventListener("visibilitychange", scheduleRefresh);
    return () => {
      live.current = false;
      window.clearTimeout(focusTimer.current);
      window.removeEventListener("focus", scheduleRefresh);
      document.removeEventListener("visibilitychange", scheduleRefresh);
    };
  }, []);

  function handlePathChange(type: ExternalResourceType) {
    versions.current[type] = (versions.current[type] ?? 0) + 1;
    dirty.current.add(type);
    setMessages(previous => ({...previous, [type]: null}));
  }
  async function handleSave(type: ExternalResourceType, input: SaveInput) {
    if (!input.path.trim()) {setError("Please enter a path."); return;}
    const version = (versions.current[type] ?? 0) + 1;
    versions.current[type] = version;
    dirty.current.delete(type);
    pendingSaves.current.set(type, version);
    setSavingType(type);
    setError(null);
    setMessages(previous => ({...previous, [type]: null}));
    try {
      await enqueue(async () => {
        if (!live.current || versions.current[type] !== version) return;
        const saved = await saveExternalResource(type, {...input, path: input.path.trim()});
        if (!live.current || versions.current[type] !== version || dirty.current.has(type)) return;
        upsert(saved);
        await check(saved, version);
      });
    } catch (cause) {
      if (live.current && versions.current[type] === version) {
        setError((cause as Error).message);
        setMessages(previous => ({...previous, [type]: (cause as Error).message}));
      }
    } finally {
      if (pendingSaves.current.get(type) === version) {
        pendingSaves.current.delete(type);
        if (live.current) setSavingType(previous => previous === type ? null : previous);
      }
    }
  }
  return {resources, loading, error, setError, savingType, pathValidationMessages, handleSave, handlePathChange};
}
