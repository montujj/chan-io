"""Nuke-specific backend for .chan file operations."""

from chan.dcc_interface import ChanDCCInterface
from typing import Tuple, Optional
import nuke
import os

class NukeChanBackend(ChanDCCInterface):
    """Nuke-specific backend for .chan file operations."""

    # Nuke doesn't have a separate shape node concept like Maya, so we can ignore the shape 
    # parameter and only require a transform (camera) node.
    REQUIRE_SHAPE = False

    def export_chan(self, path: str, node: str, shape: Optional[str], start: int, end: int) -> int:
        cam = nuke.toNode(node)
        if not cam:
            raise RuntimeError(f"Camera node '{node}' not found.")
        lines = []
        for frame in range(start, end + 1):
            nuke.frame(frame)
            tx = cam['translate'].getValueAt(frame, 0)
            ty = cam['translate'].getValueAt(frame, 1)
            tz = cam['translate'].getValueAt(frame, 2)
            rx = cam['rotate'].getValueAt(frame, 0)
            ry = cam['rotate'].getValueAt(frame, 1)
            rz = cam['rotate'].getValueAt(frame, 2)
            focal = cam['focal'].getValueAt(frame) if 'focal' in cam.knobs() else 0.0
            h_aperture = cam['haperture'].getValueAt(frame) if 'haperture' in cam.knobs() else 0.0
            v_aperture = cam['vaperture'].getValueAt(frame) if 'vaperture' in cam.knobs() else 0.0
            lines.append(
                f"{tx:.6f} {ty:.6f} {tz:.6f} {rx:.6f} {ry:.6f} {rz:.6f} "
                f"{focal:.6f} {h_aperture:.6f} {v_aperture:.6f}"
            )
        with open(path, "w") as f:
            f.write("\n".join(lines))
        return end - start + 1

    def import_chan(self, path: str, node: str) -> int:
        cam = nuke.toNode(node)
        if not cam:
            raise RuntimeError(f"Camera node '{node}' not found.")
        if not os.path.exists(path):
            raise RuntimeError(f"File '{path}' not found.")
        with open(path, "r") as f:
            lines = f.readlines()
        # Ensure all relevant knobs are set to animated and set a keyframe at the first frame
        first_frame = int(nuke.root()['first_frame'].value())
        for knob_name in ["translate", "rotate"]:
            if knob_name in cam.knobs():
                cam[knob_name].setAnimated()
                for axis in range(3):
                    value = cam[knob_name].getValueAt(first_frame, axis)
                    cam[knob_name].setValueAt(value, first_frame, axis)
        if 'focal' in cam.knobs():
            cam['focal'].setAnimated()
            value = cam['focal'].getValueAt(first_frame)
            cam['focal'].setValueAt(value, first_frame)

        for i, line in enumerate(lines):
            vals = line.strip().split()
            if len(vals) < 6:
                continue
            frame = i + first_frame
            tx, ty, tz, rx, ry, rz = map(float, vals[:6])
            cam['translate'].setValueAt(tx, frame, 0)
            cam['translate'].setValueAt(ty, frame, 1)
            cam['translate'].setValueAt(tz, frame, 2)
            cam['rotate'].setValueAt(rx, frame, 0)
            cam['rotate'].setValueAt(ry, frame, 1)
            cam['rotate'].setValueAt(rz, frame, 2)
            if len(vals) >= 9:
                focal = float(vals[6])
                h_aperture = float(vals[7])
                v_aperture = float(vals[8])
                if 'focal' in cam.knobs():
                    cam['focal'].setValueAt(focal, frame)
                if 'haperture' in cam.knobs():
                    cam['haperture'].setValue(h_aperture)
                if 'vaperture' in cam.knobs():
                    cam['vaperture'].setValue(v_aperture)
        return len(lines)

    def get_selected(self) -> Tuple[Optional[str], Optional[str]]:
        sel = nuke.selectedNodes()
        if not sel:
            return None, None
        node = sel[0].name()
        return node, None  # Nuke doesn't have shape concept

    def get_playback_range(self) -> Tuple[int, int]:
        first = int(nuke.root()['first_frame'].value())
        last = int(nuke.root()['last_frame'].value())
        return first, last


backend = NukeChanBackend()


"""
import chan
chan.ui()


import chan
from chan.nuke_io import backend as nuke_backend
chan.ui(backend=nuke_backend)
"""