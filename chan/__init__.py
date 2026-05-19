"""Chan I/O Tool: 

A utility for exporting animation channels from DCC applications 
like Maya & Nuke.

This module provides a DCC-agnostic interface and UI for exporting
animation to .chan files, which are simple text files with lines of the form:
tx ty tz rx ry rz focal_length aperture"""

# Global variable to hold the UI widget instance
_widget = None

def ui(backend=None):
    """Launch the Chan I/O Tool UI, auto-detecting DCC backend unless provided."""

    # lazy — requires PySide2 and a running DCC environment, so we delay 
    # imports until this function is called
    from ._ui import ChanExporterWidget

    global _widget
    if backend is None:
        backend = None
        try:
            import maya.cmds
            from .maya_io import backend as maya_backend
            backend = maya_backend
        except ImportError:
            pass
        if backend is None:
            try:
                import nuke
                from .nuke_io import backend as nuke_backend
                backend = nuke_backend
            except ImportError:
                pass
        if backend is None:
            try:
                import tde4
                # TO DO: Change this to tde4_io when that module is 
                # implemented, and update the import statement accordingly
                from .tdeq_io import backend as tdeq_backend
                backend = tdeq_backend
            except ImportError:
                pass

    if backend is None:
        raise RuntimeError(
            "Could not detect supported DCC environment (Maya, Nuke, or "
            "3DEqualizer). Please specify backend explicitly."
        )

    _widget = ChanExporterWidget(backend=backend)
    _widget.show()
