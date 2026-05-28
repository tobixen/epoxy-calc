import pytest
from unittest import mock


@pytest.fixture(autouse=True)
def isolated_config(tmp_path):
    """Redirect all config file operations to a temp dir so tests don't touch ~/.config."""
    with mock.patch("epoxy_calc.CONFIG_FILE", str(tmp_path / "epoxy-types.json")):
        yield
