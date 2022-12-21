from __future__ import annotations

import gettsim


def test_import():
    assert hasattr(gettsim, "__version__")
