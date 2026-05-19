"""Chan Exporter/Importer UI.

Provides a simple interface to export camera animation to a .chan file and 
import it back to a camera in Maya. The .chan file format is a simple text 
format where each line contains: tx ty tz rx ry rz focal_length aperture. The 
exporter allows you to choose the frame range (full, start/end, or single 
frame) and the importer applies the to the selected camera starting from the 
current playback start frame."""

import os

from PySide2 import QtWidgets
from . import __version__


class ChanExporterWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, backend=None):
        super(ChanExporterWidget, self).__init__(parent)
        if backend is None:
            raise RuntimeError(
                "A DCC backend must be provided to ChanExporterWidget "
                "(e.g., maya_io.backend, nuke_io.backend, etc.)"
            )
        self.backend = backend
        self.setWindowTitle(f"Chan Exporter/Importer - v {__version__}")
        self.resize(500, 180)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.tabs)
        self.export_tab = QtWidgets.QWidget()
        self.import_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.export_tab, "Export")
        self.tabs.addTab(self.import_tab, "Import")
        self._init_export_tab()
        self._init_import_tab()

    def _init_export_tab(self):
        """Set up the export tab UI."""

        layout = QtWidgets.QVBoxLayout(self.export_tab)
        file_layout = QtWidgets.QHBoxLayout()
        self.export_path = QtWidgets.QLineEdit()
        file_btn = QtWidgets.QPushButton("Browse")
        file_btn.clicked.connect(self._browse_export)
        file_layout.addWidget(QtWidgets.QLabel("Export Path:"))
        file_layout.addWidget(self.export_path)
        file_layout.addWidget(file_btn)
        layout.addLayout(file_layout)

        self.frame_group = QtWidgets.QButtonGroup(self)
        radio_layout = QtWidgets.QHBoxLayout()
        self.radio_full = QtWidgets.QRadioButton(
            "Full Frame Range (from scene)"
        )
        self.radio_startend = QtWidgets.QRadioButton("Start/End Frame")
        self.radio_single = QtWidgets.QRadioButton("Single Frame")
        self.radio_full.setChecked(True)
        self.frame_group.addButton(self.radio_full, 0)
        self.frame_group.addButton(self.radio_startend, 1)
        self.frame_group.addButton(self.radio_single, 2)
        radio_layout.addWidget(self.radio_full)
        radio_layout.addWidget(self.radio_startend)
        radio_layout.addWidget(self.radio_single)
        layout.addLayout(radio_layout)
        # Start/End/Single frame fields

        frame_fields = QtWidgets.QHBoxLayout()
        self.start_frame = QtWidgets.QSpinBox()
        self.start_frame.setRange(-100000, 100000)
        self.start_frame.setValue(1)
        self.end_frame = QtWidgets.QSpinBox()
        self.end_frame.setRange(-100000, 100000)
        self.end_frame.setValue(100)
        self.single_frame = QtWidgets.QSpinBox()
        self.single_frame.setRange(-100000, 100000)
        self.single_frame.setValue(1)
        frame_fields.addWidget(QtWidgets.QLabel("Start:"))
        frame_fields.addWidget(self.start_frame)
        frame_fields.addWidget(QtWidgets.QLabel("End:"))
        frame_fields.addWidget(self.end_frame)
        frame_fields.addWidget(QtWidgets.QLabel("Single:"))
        frame_fields.addWidget(self.single_frame)
        layout.addLayout(frame_fields)

        self.export_btn = QtWidgets.QPushButton("Export")
        self.export_btn.clicked.connect(self._export_chan)
        layout.addWidget(self.export_btn)

        layout.addWidget(
            QtWidgets.QLabel(
                ("Chan file will contain: tx ty tz rx ry rz focal_length "
                 "aperture")
            )
        )
        layout.addStretch()

        self.radio_full.toggled.connect(self._update_frame_fields)
        self.radio_startend.toggled.connect(self._update_frame_fields)
        self.radio_single.toggled.connect(self._update_frame_fields)
        self._update_frame_fields()

    def _init_import_tab(self):
        """Set up the import tab UI."""

        layout = QtWidgets.QVBoxLayout(self.import_tab)
        file_layout = QtWidgets.QHBoxLayout()
        self.import_path = QtWidgets.QLineEdit()
        file_btn = QtWidgets.QPushButton("Browse")
        file_btn.clicked.connect(self._browse_import)
        file_layout.addWidget(QtWidgets.QLabel("Import Path:"))
        file_layout.addWidget(self.import_path)
        file_layout.addWidget(file_btn)
        layout.addLayout(file_layout)
        self.import_btn = QtWidgets.QPushButton("Import")
        self.import_btn.clicked.connect(self._import_chan)
        layout.addWidget(self.import_btn)
        layout.addStretch()

    def _browse_export(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 
            "Export Chan File", 
            "", 
            "Chan Files (*.chan);;All Files (*)"
        )
        if path:
            self.export_path.setText(path)
            self.import_path.setText(path)

    def _browse_import(self):
        """Open file dialog to select .chan file for import."""

        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Import Chan File",
            "", 
            "Chan Files (*.chan);;All Files (*)"
        )
        if path:
            self.import_path.setText(path)

    def _update_frame_fields(self):
        """Enable/disable frame fields based on selected radio button."""

        self.start_frame.setEnabled(self.radio_startend.isChecked())
        self.end_frame.setEnabled(self.radio_startend.isChecked())
        self.single_frame.setEnabled(self.radio_single.isChecked())

    def _export_chan(self):
        """Export transform node animation to a .chan file."""

        path = self.export_path.text()
        if not path:
            QtWidgets.QMessageBox.warning(
                self, "Error", "Please specify export path."
            )
            return

        if self.radio_full.isChecked():
            try:
                start, end = self.backend.get_playback_range()
            except Exception:
                start, end = 1, 100
        elif self.radio_startend.isChecked():
            start = self.start_frame.value()
            end = self.end_frame.value()
        else:
            start = end = self.single_frame.value()

        try:
            trn, shape = self.backend.get_selected()

            # Only require shape if the backend needs it (e.g. Maya).
            # Nuke has no shape concept so we only need the transform.
            require_shape = (
                hasattr(self.backend, "REQUIRE_SHAPE")
                and self.backend.REQUIRE_SHAPE
            )

            if not trn or (require_shape and not shape):
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    f"Select a transform node"
                    f"{' (and shape)' if require_shape else ''}"
                    f" to export chan file.",
                )
                return

            num_frames = self.backend.export_chan(
                path,
                trn,
                shape,
                start,
                end
            )
            QtWidgets.QMessageBox.information(
                self, 
                "Success",
                f"Exported {num_frames} frames to {path}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", str(e)
            )

    def _show_import_preview(self, lines):
        msg = "".join(lines[:10]) if lines else "File is empty."
        preview_dialog = QtWidgets.QDialog(self)
        preview_dialog.setWindowTitle("Import Preview")
        preview_dialog.resize(700, 200)
        layout = QtWidgets.QVBoxLayout(preview_dialog)
        text_edit = QtWidgets.QPlainTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(msg)
        layout.addWidget(text_edit)
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok
        )
        btn_box.accepted.connect(preview_dialog.accept)
        layout.addWidget(btn_box)
        preview_dialog.exec_()

    def _import_chan(self):
        """Import a .chan file & apply animation to selected transform node."""

        path = self.import_path.text()
        if not path or not os.path.exists(path):
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                "Please specify a valid import path."
            )
            return
        try:
            with open(path, "r") as f:
                lines = f.readlines()
            self._show_import_preview(lines)
            trn, _ = self.backend.get_selected()
            if not trn:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    "Select a transform node to import to."
                )
                return
            self.backend.import_chan(path, trn)
            QtWidgets.QMessageBox.information(
                self, 
                "Success",
                f"Imported chan file to {trn}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", str(e)
            )
