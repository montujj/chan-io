# Changelog

All notable changes to Chan I/O are documented here.

---

## [1.1.0] - 2026-05-18

### Fixed
- CI pipeline failing on Ubuntu 24.04 — removed Python 3.7 from test matrix
  (EOL since June 2023, no longer available on Ubuntu 24.04) and replaced
  with 3.9, 3.11, 3.12
- `chan.ui()` becoming uncallable after first invocation — caused by a name
  collision between the `ui()` function in `__init__.py` and the `chan/ui.py`
  submodule; fixed by renaming `ui.py` to `_ui.py`
- `PySide2` removed from `install_requires` — PySide2's last release only
  supports up to Python 3.10 and cannot be pip-installed on 3.11+; it is
  also bundled by the DCC host (Maya/Nuke) so pip should never install it
- Top-level PySide2 import in `__init__.py` made lazy so the `chan` package
  can be imported in any environment without Qt installed
- Removed broken CI verify steps for `maya_io` and `nuke_io` — those modules
  require the actual DCC software and cannot be imported in CI

### Changed
- `chan/ui.py` renamed to `chan/_ui.py` to mark it as internal and avoid the
  module/function name collision
- `self.layout` in `ChanExporterWidget` renamed to `self.main_layout` to avoid
  shadowing the built-in `QWidget.layout()` method
- Version bumped to `1.1.0` in `setup.py`
- Added `__version__ = "1.1.0"` to `chan/__init__.py` for runtime version access

### Code Quality
- Fixed PEP 8 import ordering in `_ui.py` (stdlib before third-party)
- Removed unused `ChanDCCInterface` import from `_ui.py`
- Removed commented-out dead code in `_ui.py`
- Replaced `.format()` string with f-string for consistency
- Reformatted long lines in `maya_io.py` and `_ui.py` to stay under 79 characters
- Applied Black formatter to `_ui.py`

### Docs
- Added Screenshots section to `README.md` with Export and Import tab previews
- Updated project structure in `README.md` to reflect `_ui.py` rename

---

## [1.0.0] - 2026-05-01

### Added
- Initial release of Chan I/O Tool
- Maya backend (`maya_io.py`) — export and import `.chan` camera animation files
- Nuke backend (`nuke_io.py`) — export and import `.chan` camera animation files
- Abstract DCC interface (`dcc_interface.py`) for adding future DCC backends
- PySide2 UI with Export and Import tabs, frame range options, and import preview
- Auto-detection of DCC environment on `chan.ui()` launch
- Full test suite with pytest covering Maya, Nuke, and interface backends
- CI/CD pipeline via GitHub Actions across Python 3.9, 3.11, 3.12
- Support for camera data: translation, rotation, focal length, aperture (h/v)
