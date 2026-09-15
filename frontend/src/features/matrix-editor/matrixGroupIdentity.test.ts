import { describe, expect, it } from "vitest";

import {
  allocateManualGroupIdentity,
  findDuplicateMatrixGroupKeys,
} from "./matrixGroupIdentity";

describe("Matrix group identity", () => {
  it("allocates a new stable id and key without reusing positional identities", () => {
    const identity = allocateManualGroupIdentity([
      { id: "group-1", groupKey: "g1" },
      { id: "group-3", groupKey: "manual_group_1" },
      { id: "source-group-2", groupKey: "manual_group_3" },
    ]);

    expect(identity).toEqual({ id: "group-4", groupKey: "manual_group_4" });
  });

  it("identifies every group that shares a persisted group key", () => {
    const result = findDuplicateMatrixGroupKeys([
      { id: "group-a", groupKey: "g1" },
      { id: "group-b", groupKey: " g1 " },
      { id: "group-c", groupKey: "g2" },
    ]);

    expect(result.duplicateGroupIds).toEqual(new Set(["group-a", "group-b"]));
    expect(result.duplicateKeys).toEqual(["g1"]);
  });
});
