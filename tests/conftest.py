import pytest
from unittest import mock


@pytest.fixture(autouse=True)
def isolated_config(tmp_path):
    """Redirect the config and log files to a temp dir so tests don't touch the real ones."""
    with mock.patch("epoxy_calc.CONFIG_FILE", str(tmp_path / "epoxy-types.json")), \
            mock.patch("epoxy_calc.DEFAULT_LOG_FILE", str(tmp_path / "epoxy.log")):
        yield
