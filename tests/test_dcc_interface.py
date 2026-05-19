"""Tests for the abstract DCC interface."""

import pytest
from chan.dcc_interface import ChanDCCInterface


def test_cannot_instantiate_abstract_class():
    """ChanDCCInterface should not be instantiable directly."""
    with pytest.raises(TypeError):
        ChanDCCInterface()


def test_abstract_methods_exist():
    """ChanDCCInterface should define all required abstract methods."""
    abstract_methods = ChanDCCInterface.__abstractmethods__
    assert "export_chan" in abstract_methods
    assert "import_chan" in abstract_methods
    assert "get_selected" in abstract_methods
    assert "get_playback_range" in abstract_methods


def test_concrete_class_must_implement_all_methods():
    """A subclass that does not implement all abstract methods should raise TypeError."""
    class IncompleteDCCBackend(ChanDCCInterface):
        def export_chan(self, path, node, shape, start, end):
            pass
        # Missing import_chan, get_selected, get_playback_range

    with pytest.raises(TypeError):
        IncompleteDCCBackend()


def test_concrete_class_can_be_instantiated():
    """A fully implemented subclass should instantiate without errors."""
    class CompleteDCCBackend(ChanDCCInterface):
        def export_chan(self, path, node, shape, start, end):
            return 0
        def import_chan(self, path, node):
            return 0
        def get_selected(self):
            return None, None
        def get_playback_range(self):
            return 1, 100

    backend = CompleteDCCBackend()
    assert backend is not None
