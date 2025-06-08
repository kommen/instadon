import pytest
from instadon.core import InstaDon

def test_instadon_initialization():
    """Test that InstaDon can be initialized."""
    app = InstaDon()
    assert app is not None
