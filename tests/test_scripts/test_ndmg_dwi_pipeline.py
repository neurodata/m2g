""" First pytest file for ndmg. Basic assertions that don't mean anything for now just to make sure pytest + travis works."""

import pytest
import ndmg



def foo():
    raise ValueError("Testing Travis")

def test_foo():
    with pytest.raises(ValueError):
        foo()