"""Application service for runtime projection read-only snapshot retrieval."""

from __future__ import annotations

from backend.modules.runtime_projection.snapshot_adapter import (
    RuntimeProjectionSnapshot,
    SnapshotBuildInput,
    build_runtime_projection_snapshot,
)


class RuntimeProjectionReadOnlyService:
    """Thin application-layer orchestrator for read-only runtime projection snapshots."""

    def build_snapshot(
        self,
        build_input: SnapshotBuildInput,
    ) -> RuntimeProjectionSnapshot:
        """Return one deterministic snapshot from current projection adapter outputs."""
        return build_runtime_projection_snapshot(build_input)

