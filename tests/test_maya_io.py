"""Tests for Maya-specific Chan I/O backend."""

import pytest
import sys
from unittest.mock import MagicMock, patch

# Mock maya and maya.cmds before importing maya_io
# This is required because Maya is not available in CI environment
maya_mock = MagicMock()
sys.modules['maya'] = maya_mock
sys.modules['maya.cmds'] = maya_mock.cmds

from chan.maya_io import MayaChanBackend


@pytest.fixture
def backend():
    """Create a fresh MayaChanBackend instance for each test."""
    return MayaChanBackend()


# --- Backend properties ---

def test_require_shape_is_true(backend):
    """Maya backend should require a shape node."""
    assert backend.REQUIRE_SHAPE is True


# --- get_playback_range ---

def test_get_playback_range_returns_tuple(backend):
    """get_playback_range should return a tuple of two ints."""
    with patch('chan.maya_io.cmds') as mock_cmds:
        mock_cmds.playbackOptions.side_effect = lambda **kwargs: (
            1 if kwargs.get('min') else 100
        )
        start, end = backend.get_playback_range()
        assert isinstance(start, int)
        assert isinstance(end, int)


def test_get_playback_range_values(backend):
    """get_playback_range should return correct start and end frames."""
    with patch('chan.maya_io.cmds') as mock_cmds:
        mock_cmds.playbackOptions.side_effect = lambda **kwargs: (
            1 if kwargs.get('min') else 100
        )
        start, end = backend.get_playback_range()
        assert start == 1
        assert end == 100


# --- get_selected ---

def test_get_selected_no_selection_returns_none(backend):
    """get_selected should return None, None when nothing is selected."""
    with patch('chan.maya_io.cmds') as mock_cmds:
        mock_cmds.ls.return_value = []
        node, shape = backend.get_selected()
        assert node is None
        assert shape is None


def test_get_selected_camera_returns_node_and_shape(backend):
    """get_selected should return node and camera shape when camera is selected."""
    with patch('chan.maya_io.cmds') as mock_cmds:
        mock_cmds.ls.return_value = ['camera1']
        mock_cmds.listRelatives.side_effect = lambda *args, **kwargs: (
            ['cameraShape1'] if kwargs.get('type') == 'camera' else []
        )
        node, shape = backend.get_selected()
        assert node == 'camera1'
        assert shape == 'cameraShape1'


def test_get_selected_mesh_returns_node_and_shape(backend):
    """get_selected should return node and mesh shape when mesh is selected."""
    with patch('chan.maya_io.cmds') as mock_cmds:
        mock_cmds.ls.return_value = ['pSphere1']
        mock_cmds.listRelatives.side_effect = lambda *args, **kwargs: (
            [] if kwargs.get('type') == 'camera'
            else ['pSphereShape1'] if kwargs.get('type') == 'mesh'
            else []
        )
        node, shape = backend.get_selected()
        assert node == 'pSphere1'
        assert shape == 'pSphereShape1'


def test_get_selected_transform_only(backend):
    """get_selected should return node with None shape for plain transform."""
    with patch('chan.maya_io.cmds') as mock_cmds:
        mock_cmds.ls.return_value = ['locator1']
        mock_cmds.listRelatives.return_value = []
        node, shape = backend.get_selected()
        assert node == 'locator1'
        assert shape is None


# --- export_chan ---

def test_export_chan_returns_correct_frame_count(backend, tmp_path):
    """export_chan should return the correct number of exported frames."""
    output_file = str(tmp_path / "test.chan")
    with patch('chan.maya_io.cmds') as mock_cmds:
        mock_cmds.nodeType.return_value = 'camera'
        mock_cmds.xform.side_effect = lambda *a, **kw: (
            [1.0, 2.0, 3.0] if kw.get('translation') else [10.0, 20.0, 30.0]
        )
        mock_cmds.getAttr.return_value = 35.0
        num_frames = backend.export_chan(output_file, 'camera1', 'cameraShape1', 1, 5)
        assert num_frames == 5


def test_export_chan_writes_correct_line_count(backend, tmp_path):
    """export_chan should write one line per frame."""
    output_file = str(tmp_path / "test.chan")
    with patch('chan.maya_io.cmds') as mock_cmds:
        mock_cmds.nodeType.return_value = 'camera'
        mock_cmds.xform.side_effect = lambda *a, **kw: (
            [1.0, 2.0, 3.0] if kw.get('translation') else [10.0, 20.0, 30.0]
        )
        mock_cmds.getAttr.return_value = 35.0
        backend.export_chan(output_file, 'camera1', 'cameraShape1', 1, 5)
        with open(output_file) as f:
            lines = f.readlines()
        assert len(lines) == 5


def test_export_chan_file_contains_nine_values(backend, tmp_path):
    """Each line in exported .chan file should contain 9 values for a camera."""
    output_file = str(tmp_path / "test.chan")
    with patch('chan.maya_io.cmds') as mock_cmds:
        mock_cmds.nodeType.return_value = 'camera'
        mock_cmds.xform.side_effect = lambda *a, **kw: (
            [1.0, 2.0, 3.0] if kw.get('translation') else [10.0, 20.0, 30.0]
        )
        mock_cmds.getAttr.return_value = 35.0
        backend.export_chan(output_file, 'camera1', 'cameraShape1', 1, 3)
        with open(output_file) as f:
            lines = f.readlines()
        for line in lines:
            values = line.strip().split()
            assert len(values) == 9


def test_export_chan_single_frame(backend, tmp_path):
    """export_chan with same start and end should write exactly 1 line."""
    output_file = str(tmp_path / "test.chan")
    with patch('chan.maya_io.cmds') as mock_cmds:
        mock_cmds.nodeType.return_value = 'transform'
        mock_cmds.xform.side_effect = lambda *a, **kw: (
            [0.0, 0.0, 0.0] if kw.get('translation') else [0.0, 0.0, 0.0]
        )
        mock_cmds.getAttr.return_value = 0.0
        num_frames = backend.export_chan(output_file, 'locator1', None, 5, 5)
        assert num_frames == 1
        with open(output_file) as f:
            lines = f.readlines()
        assert len(lines) == 1
