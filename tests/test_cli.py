import pytest
from click.testing import CliRunner
from ghia.cli import click_validate_reposlug
from ghia.cli import main_cmd
from helpers import config


def test_validate_reposlug():
    with pytest.raises(Exception):
        click_validate_reposlug(None, None, "abcdef")
    assert "abc/def" == click_validate_reposlug(None, None, "abc/def")


def test_run():
    runner = CliRunner()
    result = runner.invoke(main_cmd, f"-a {config('auth')} -r {config('rules')} abc/def")
    print(result.output)
    assert result.exit_code == 10
    assert "Could not list issues" in result.output
