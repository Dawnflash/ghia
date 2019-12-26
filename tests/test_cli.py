import pytest
from click.testing import CliRunner
from ghia.cli import click_validate_reposlug
from ghia.cli import main_cmd
from helpers import fixture


def test_validate_reposlug():
    with pytest.raises(Exception):
        click_validate_reposlug(None, None, "abcdef")
    assert ["abc/def"] == click_validate_reposlug(None, None, ["abc/def"])


def test_run():
    runner = CliRunner()
    param = f"-a {fixture('auth.cfg')} -r {fixture('rules.cfg')} abc/def"
    result = runner.invoke(main_cmd, param)
    print(result.output)
    assert result.exit_code == 10
    assert "Could not list issues" in result.output
