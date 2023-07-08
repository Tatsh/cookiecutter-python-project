"""Configuration for Pytest."""
from typing import NoReturn
import os

{% if cookiecutter.want_main %}
from click.testing import CliRunner
{% endif %}
import pytest

if os.getenv('_PYTEST_RAISE', '0') != '0':  # pragma no cover

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call: pytest.CallInfo[None]) -> NoReturn:
        assert call.excinfo is not None
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo: pytest.ExceptionInfo[BaseException]) -> NoReturn:
        raise excinfo.value

{% if cookiecutter.want_main %}
@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()
{% endif %}
