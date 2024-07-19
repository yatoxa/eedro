from eedro import __version__, get_version


def test_get_version():
    assert get_version() == __version__.VERSION
