import pathlib

import pytest

from eedro.contrib.utils import import_string


def test_import_string_returns_attribute():
    resolved = import_string("pathlib.Path")
    assert resolved is pathlib.Path


def test_import_string_raises_for_incorrect_path_format():
    with pytest.raises(ImportError, match="does not look like a module path"):
        import_string("pathlib")


def test_import_string_raises_for_missing_attribute():
    with pytest.raises(ImportError, match='does not define a "MissingAttr" attribute'):
        import_string("pathlib.MissingAttr")
