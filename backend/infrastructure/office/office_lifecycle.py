"""Office automation lifecycle boundary.

ConnLab prefers file-level parsers. COM automation is intentionally kept behind
this boundary for future fallback work.
"""

from __future__ import annotations


class OfficeAutomationUnavailable(RuntimeError):
    """Raised when a COM fallback is requested before it is implemented."""


class OfficeLifecycleManager:
    """Centralize future COM automation lifecycle management."""

    def require_com_fallback(self, application_name: str) -> None:
        """Reject COM fallback until a task explicitly implements it."""
        raise OfficeAutomationUnavailable(
            f"{application_name} COM fallback is not implemented in this phase."
        )
