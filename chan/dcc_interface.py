"""DCC-agnostic interface for .chan file operations."""

from abc import ABC, abstractmethod
from typing import Tuple, Optional


class ChanDCCInterface(ABC):
    """Abstract base class defining the interface for DCC-specific backends
    to implement .chan file export/import and scene queries."""

    @abstractmethod
    def export_chan(
        self, path: str, node: str, shape: Optional[str], start: int, end: int
    ) -> int:
        """Export animation from the given node to a .chan file."""
        pass

    @abstractmethod
    def import_chan(self, path: str, node: str) -> int:
        """Import a .chan file & apply animation to the given node in the DCC."""
        pass

    @abstractmethod
    def get_selected(self) -> Tuple[Optional[str], Optional[str]]:
        """Return the currently selected transform node and its shape (if any)."""
        pass

    @abstractmethod
    def get_playback_range(self) -> Tuple[int, int]:
        """Return the current playback frame range in the DCC (start, end)."""
        pass
