from super_mcp import __version__


def test_scaffold_version_is_pre_release() -> None:
    assert __version__ == "0.0.0"
