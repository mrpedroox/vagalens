from typer.testing import CliRunner

import vagalens
from vagalens.cli import app

runner = CliRunner()


def test_version_string() -> None:
    assert vagalens.__version__


def test_cli_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert vagalens.__version__ in result.output


def test_cli_config_prints_json() -> None:
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert '"llm"' in result.output
