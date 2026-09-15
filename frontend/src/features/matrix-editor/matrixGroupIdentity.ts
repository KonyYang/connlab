export type MatrixGroupIdentitySource = {
  id: string;
  groupKey: string;
};

export type MatrixGroupIdentity = {
  id: string;
  groupKey: string;
};

export type DuplicateMatrixGroupKeys = {
  duplicateGroupIds: Set<string>;
  duplicateKeys: string[];
};

export function allocateManualGroupIdentity(
  groups: readonly MatrixGroupIdentitySource[],
): MatrixGroupIdentity {
  const usedIds = new Set(groups.map((group) => group.id.trim()));
  const usedKeys = new Set(groups.map((group) => group.groupKey.trim()));
  let idSequence = maximumSequence(usedIds, /^group-(\d+)$/i) + 1;
  let keySequence = maximumSequence(usedKeys, /^manual_group_(\d+)$/i) + 1;

  while (usedIds.has(`group-${idSequence}`)) idSequence += 1;
  while (usedKeys.has(`manual_group_${keySequence}`)) keySequence += 1;

  return {
    id: `group-${idSequence}`,
    groupKey: `manual_group_${keySequence}`,
  };
}

export function findDuplicateMatrixGroupKeys(
  groups: readonly MatrixGroupIdentitySource[],
): DuplicateMatrixGroupKeys {
  const groupIdsByKey = new Map<string, string[]>();
  groups.forEach((group) => {
    const key = group.groupKey.trim();
    if (!key) return;
    const groupIds = groupIdsByKey.get(key) ?? [];
    groupIds.push(group.id);
    groupIdsByKey.set(key, groupIds);
  });

  const duplicateGroupIds = new Set<string>();
  const duplicateKeys: string[] = [];
  groupIdsByKey.forEach((groupIds, key) => {
    if (groupIds.length < 2) return;
    duplicateKeys.push(key);
    groupIds.forEach((groupId) => duplicateGroupIds.add(groupId));
  });
  return { duplicateGroupIds, duplicateKeys };
}

function maximumSequence(values: ReadonlySet<string>, pattern: RegExp): number {
  let maximum = 0;
  values.forEach((value) => {
    const match = value.match(pattern);
    if (!match) return;
    maximum = Math.max(maximum, Number(match[1]));
  });
  return maximum;
}
