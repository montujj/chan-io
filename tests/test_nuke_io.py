"""Tests for Nuke-specific Chan I/O backend."""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch, mock_open

# Mock nuke before importing nuke_io
# This is required because Nuke is not available in CI environment
nuke_mock = MagicMock()
sys.modules['nuke'] = nuke_mock

from chan.nuke_io import NukeChanBackend


@pytest.fixture
def backend():
    """Create a fresh NukeChanBackend instance for each test."""
    return NukeChanBackend()


# --- Backend properties ---

def test_require_shape_is_false(backend):
    """Nuke backend should NOT require a shape node."""
    assert backend.REQUIRE_SHAPE is False


# --- get_selected ---

def test_get_selected_no_selection_returns_none(backend):
    """get_selected should return None, None when nothing is selected."""
    with patch('chan.nuke_io.nuke') as mock_nuke:
        mock_nuke.selectedNodes.return_value = []
        node, shape = backend.get_selected()
        assert node is None
        assert shape is None


def test_get_selected_returns_node_name(backend):
    """get_selected should return the name of the first selected node."""
    with patch('chan.nuke_io.nuke') as mock_nuke:
        mock_node = MagicMock()
        mock_node.name.return_value = 'Camera1'
        mock_nuke.selectedNodes.return_value = [mock_node]
        node, shape = backend.get_selected()
        assert node == 'Camera1'


def test_get_selected_shape_is_always_none(backend):
    """Nuke backend should always return None for shape."""
    with patch('chan.nuke_io.nuke') as mock_nuke:
        mock_node = MagicMock()
        mock_node.name.return_value = 'Camera1'
        mock_nuke.selectedNodes.return_value = [mock_node]
        node, shape = backend.get_selected()
        assert shape is None


# --- get_playback_range ---

def test_get_playback_range_returns_tuple(backend):
    """get_playback_range should return a tuple of two ints."""
    with patch('chan.nuke_io.nuke') as mock_nuke:
        mock_root = MagicMock()
        mock_first = MagicMock()
        mock_last = MagicMock()
        mock_first.value.return_value = 1
        mock_last.value.return_value = 100
        mock_root.__getitem__ = lambda self, k: (
            mock_first if k == 'first_frame' else mock_last
        )
        mock_nuke.root.return_value = mock_root
        start, end = backend.get_playback_range()
        assert isinstance(start, int)
        assert isinstance(end, int)


# --- export_chan ---

def test_export_chan_raises_if_node_not_found(backend, tmp_path):
    """export_chan should raise RuntimeError if camera node is not found."""
    output_file = str(tmp_path / "test.chan")
    with patch('chan.nuke_io.nuke') as mock_nuke:
        mock_nuke.toNode.return_value = None
        with pytest.raises(RuntimeError, match="not found"):
            backend.export_chan(output_file, 'NonExistentCamera', None, 1, 5)


def test_export_chan_returns_correct_frame_count(backend, tmp_path):
    """export_chan should return the correct number of exported frames."""
    output_file = str(tmp_path / "test.chan")
    with patch('chan.nuke_io.nuke') as mock_nuke:
        mock_cam = MagicMock()
        mock_cam.knobs.return_value = ['translate', 'rotate', 'focal', 'haperture', 'vaperture']
        mock_cam['translate'].getValueAt.return_value = 1.0
        mock_cam['rotate'].getValueAt.return_value = 0.0
        mock_cam['focal'].getValueAt.return_value = 35.0
        mock_cam['haperture'].getValueAt.return_value = 24.0
        mock_cam['vaperture'].getValueAt.return_value = 18.0
        mock_nuke.toNode.return_value = mock_cam
        num_frames = backend.export_chan(output_file, 'Camera1', None, 1, 5)
        assert num_frames == 5


# --- import_chan ---

def test_import_chan_raises_if_node_not_found(backend, tmp_path):
    """import_chan should raise RuntimeError if camera node is not found."""
    chan_file = str(tmp_path / "test.chan")
    with open(chan_file, 'w') as f:
        f.write("1.0 2.0 3.0 10.0 20.0 30.0 35.0 24.0 18.0\n")
    with patch('chan.nuke_io.nuke') as mock_nuke:
        mock_nuke.toNode.return_value = None
        with pytest.raises(RuntimeError, match="not found"):
            backend.import_chan(chan_file, 'NonExistentCamera')


def test_import_chan_raises_if_file_not_found(backend, tmp_path):
    """import_chan should raise RuntimeError if .chan file does not exist."""
    with patch('chan.nuke_io.nuke') as mock_nuke:
        mock_cam = MagicMock()
        mock_nuke.toNode.return_value = mock_cam
        with pytest.raises(RuntimeError, match="not found"):
            backend.import_chan("/nonexistent/path/fake.chan", 'Camera1')
