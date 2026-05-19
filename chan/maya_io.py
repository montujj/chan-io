"""Maya-specific logic for exporting and importing .chan camera files."""

from maya import cmds
from chan.dcc_interface import ChanDCCInterface


class MayaChanBackend(ChanDCCInterface):
    """Maya-specific backend for .chan file operations."""

    # This backend requires a shape node (camera or mesh) to determine if it's 
    # exporting a camera or regular transform, which affects the .chan format.

    REQUIRE_SHAPE = True

    def export_chan(
        self, path: str, node: str, shape: str, start: int, end: int
    ) -> int:
        """Export animation in worldspace to a .chan file.

        For cameras: tx ty tz rx ry rz focal_length h_aperture v_aperture
        For regular transforms: tx ty tz rx ry rz 0 0 0.

        Args:
            path (str): Path to save the .chan file.
            node (str): Name of the transform node to export.
            shape (str or None): Name of the shape node (camera or mesh) 
                                 if present, otherwise None.
            start (int): Start frame for export.
            end (int): End frame for export.
        """

        hap = "horizontalFilmAperture"
        vap = "verticalFilmAperture"
        is_camera = False
        if shape:
            shape_type = cmds.nodeType(shape)
            if shape_type == "camera":
                is_camera = True
        lines = []
        cmds.refresh(suspend=True)
        for frame in range(start, end + 1):
            cmds.currentTime(frame)
            translate_xyz = cmds.xform(
                node,
                query=True,
                worldSpace=True,
                translation=True
            )
            rotate_xyz = cmds.xform(
                node,
                query=True,
                worldSpace=True,
                rotation=True
            )
            tx, ty, tz = translate_xyz
            rx, ry, rz = rotate_xyz
            if is_camera:
                focal = cmds.getAttr(f"{shape}.focalLength")
                # Maya stores aperture in inches, but we want to export in mm
                # for .chan files, so convert here.
                h_aperture = cmds.getAttr(f"{shape}.{hap}") * 25.4
                v_aperture = cmds.getAttr(f"{shape}.{vap}") * 25.4
            else:
                focal = 0.0
                h_aperture = 0.0
                v_aperture = 0.0

            lines.append(
                f"{tx:.6f} {ty:.6f} {tz:.6f} "
                f"{rx:.6f} {ry:.6f} {rz:.6f} "
                f"{focal:.6f} {h_aperture:.6f} {v_aperture:.6f}"
            )

        with open(path, "w") as fstream:
            fstream.write("\n".join(lines))
        cmds.refresh(suspend=False)
        return end - start + 1

    def import_chan(self, path: str, node: str) -> int:
        """Import a .chan file and apply animation to the given node in Maya.
        If node is a camera, set all fields. If not, set only tx, ty, tz, rx, ry, rz.

        Args:
            path (str): Path to the .chan file.
            node (str): Name of the transform node to apply animation to.
        """

        shape = cmds.listRelatives(node, shapes=True, type="camera")
        is_camera = bool(shape)
        if is_camera:
            shape = shape[0]

        with open(path, "r") as f:
            lines = f.readlines()
        frame = int(cmds.playbackOptions(query=True, min=True))

        for i, line in enumerate(lines):
            vals = line.strip().split()
            if len(vals) < 6:
                continue

            tx, ty, tz, rx, ry, rz = map(float, vals[:6])
            cmds.setKeyframe(node, attribute="translateX", value=tx, time=frame + i)
            cmds.setKeyframe(node, attribute="translateY", value=ty, time=frame + i)
            cmds.setKeyframe(node, attribute="translateZ", value=tz, time=frame + i)
            cmds.setKeyframe(node, attribute="rotateX", value=rx, time=frame + i)
            cmds.setKeyframe(node, attribute="rotateY", value=ry, time=frame + i)
            cmds.setKeyframe(node, attribute="rotateZ", value=rz, time=frame + i)
            if is_camera and len(vals) >= 9:
                focal = float(vals[6])
                h_aperture = float(vals[7])
                v_aperture = float(vals[8])
                cmds.setKeyframe(shape, attribute="focalLength", value=focal, time=frame + i)
                if i == 0:
                    cmds.setAttr(f"{shape}.{hap}", h_aperture / 25.4)
                    cmds.setAttr(f"{shape}.{vap}", v_aperture / 25.4)

        # Force Maya to update the viewport and timeline after import
        cmds.currentTime(cmds.currentTime(q=True))
        return len(lines)

    def get_selected(self):
        """Get the first selected transform node & check if it has a camera 
        shape or mesh shape."""

        sel = cmds.ls(selection=True, type="transform")
        if not sel:
            return None, None

        node = sel[0]
        shape = cmds.listRelatives(node, shapes=True, type="camera")
        if shape:
            return node, shape[0]
        shape = cmds.listRelatives(node, shapes=True, type="mesh")
        if shape:
            return node, shape[0]

        return node, None

    def get_playback_range(self):
        """Get the current playback range from Maya.

        Returns:
            tuple[int, int]: The start & end frames of current playback range.
        """

        start = int(cmds.playbackOptions(query=True, min=True))
        end = int(cmds.playbackOptions(query=True, max=True))
        return start, end


backend = MayaChanBackend()


"""
import chan
chan.ui()

# 
import chan
from chan.maya_io import backend as maya_backend
chan.ui(backend=maya_backend)
"""