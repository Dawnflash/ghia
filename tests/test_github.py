import betamax
import pytest
import os
import io
from contextlib import redirect_stdout
from ghia.github import get_gh_login, gather_issues, process_issue
from helpers import auth_default, issue_configs, fetch_issue, get_repo, get_user


with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'


@pytest.fixture
def issues(betamax_session):
    token, repo = auth_default()[0], get_repo()
    return gather_issues(betamax_session, repo, token)


def test_get_login(betamax_session):
    token, user = auth_default()[0], get_user()
    assert get_gh_login(betamax_session, token) == user


def test_get_issues(issues):
    assert len(issues) == 112


@pytest.mark.parametrize("issue_no,config,counts,label", issue_configs())
def test_process_issue(issue_no, config, counts, label,
                       betamax_parametrized_session, issues):
    issue = fetch_issue(issues, issue_no)
    if issue is None:
        pytest.skip(f"Issue #{issue_no} not found")

    f = io.StringIO()
    with redirect_stdout(f):
        assert process_issue(betamax_parametrized_session, issue, config, True)
    fval = f.getvalue()
    print(fval)
    print(issue['body'])
    sub, add, equ = counts
    for line in fval.splitlines():
        if line.startswith("   -"):
            sub -= 1
        elif line.startswith("   +"):
            add -= 1
        elif line.startswith("   ="):
            equ -= 1
    assert (sub, add, equ) == (0, 0, 0)
    if label:
        assert "FALLBACK" in fval
        assert label in fval
    else:
        assert "FALLBACK" not in fval
