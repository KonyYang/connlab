import type { TemperatureWorkspaceDraft } from './temperatureWorkspace';

// This database contains only the replaceable Tools draft, never project records or source paths.
const DATABASE = 'connlab-temperature-workspace';
let connection: Promise<IDBDatabase> | undefined;
let source: Pick<TemperatureWorkspaceDraft['tool'], 'file' | 'table'> | undefined;

function openDatabase(): Promise<IDBDatabase> {
  if (connection) return connection;
  connection = new Promise((resolve, reject) => {
    const request = indexedDB.open(DATABASE, 1);
    request.onupgradeneeded = () => request.result.createObjectStore('workspace');
    request.onsuccess = () => {
      const database = request.result;
      database.onversionchange = () => { database.close(); connection = undefined; source = undefined; };
      resolve(database);
    };
    request.onerror = () => reject(request.error);
    request.onblocked = () => reject(new Error('Workspace storage is busy.'));
  });
  void connection.catch(() => { connection = undefined; });
  return connection;
}

function completed(transaction: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve();
    transaction.onabort = () => reject(transaction.error ?? new Error('Workspace storage was interrupted.'));
    transaction.onerror = () => reject(transaction.error);
  });
}

export async function readTemperatureWorkspace(): Promise<TemperatureWorkspaceDraft | null> {
  const database = await openDatabase();
  const transaction = database.transaction('workspace', 'readonly');
  const done = completed(transaction);
  const store = transaction.objectStore('workspace');
  const draft = store.get('draft');
  const original = store.get('source');
  await done;
  if (!draft.result) return null;
  const tool = draft.result.tool;
  if (draft.result.version !== 1 || !tool || typeof tool.previewId !== 'string' || !draft.result.report || !original.result
      || !['targetRise', 'maxTemperature', 'step', 'ambientPoint'].every(key => typeof tool[key] === 'string')
      || typeof tool.zeroIntercept !== 'boolean' || typeof tool.confirmed !== 'boolean'
      || (!Array.isArray(original.result.table?.rows) && original.result.table !== null)
      || (original.result.file !== null && (!(original.result.file instanceof Blob) || typeof original.result.fileName !== 'string'))
      || (tool.selection !== null && (!tool.selection || !Array.isArray(tool.selection.excluded_rows) || !Array.isArray(tool.selection.temperature_columns)))) {
    throw new Error('This saved workspace cannot be read by this version.');
  }
  const { file, table } = original.result;
  // Some hosts deserialize a File as a Blob; keep its explicit upload name as well.
  const restoredFile = file ? new File([file], original.result.fileName, { type: file.type, lastModified: original.result.lastModified }) : null;
  source = { file: restoredFile, table };
  return { ...draft.result, tool: { ...tool, file: restoredFile, table, busy: null,
    error: draft.result.interrupted ? 'The previous operation was interrupted. Retry it to continue.' : null } };
}

export async function writeTemperatureWorkspace(value: TemperatureWorkspaceDraft): Promise<void> {
  const database = await openDatabase();
  const transaction = database.transaction('workspace', 'readwrite');
  const done = completed(transaction);
  const store = transaction.objectStore('workspace');
  const { file, table, busy, error: _error, ...tool } = value.tool;
  const changedSource = !source || source.file !== file || source.table !== table;
  try {
    if (changedSource) store.put({ file, table, fileName: file?.name, lastModified: file?.lastModified }, 'source');
    store.put({ ...value, tool, interrupted: Boolean(busy) }, 'draft');
  } catch (error) {
    transaction.abort();
    await done.catch(() => undefined);
    throw error;
  }
  await done;
  if (changedSource) source = { file, table };
}

export async function clearTemperatureWorkspace(): Promise<void> {
  const database = await openDatabase();
  const transaction = database.transaction('workspace', 'readwrite');
  const done = completed(transaction);
  transaction.objectStore('workspace').clear();
  await done;
  source = undefined;
}
