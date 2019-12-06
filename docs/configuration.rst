Configuration
#############

GHIA configuration splits into two categories:

* :ref:`github_access`
* :ref:`assignment_logic`

The configuration is placed in config files with INI syntax.

.. _github_access:

GitHub access
-------------

The package communicates with the GitHub API and needs an access token to access user data and issues.
You will need to get a Personal access token for a GitHub account with access to your target repos.

To create one, follow `this link <https://github.com/settings/tokens>`_.
You will need a token with ``repo`` and ``read:user`` scopes.
To achieve this, check the respective checkboxes in the ``edit token`` view.

The access token is a 40-character hexstring. Put it down, GitHub will only show it to you once.

Optionally, you may set a webhook secret. See the :ref:`usage_webhook` section for details.

Structure of ``access.cfg``:

.. code:: ini

    [github]
    # required
    token=01234567890abcdef0123456789abcdef0123456
    # optional
    secret=youcanauthenticategithubhookswiththis

.. _assignment_logic:

Assignment logic
----------------

This is where you define your assignment policy - who will you assign to and when.

You define the assignment policy as pairs of GitHub users and rule arrays.
The rules themselves are pairs of ``subject:needle``.

The needle is a regular expression defining what to match and the subject defines where to match it.
See the full config example below for details.

What subjects can you match against?

* **title**
* **text** (the issue body)
* **label**
* **any** (any of the above)

Optionally, you may set a fallback label which gets automatically assigned to unassigned issues with no matching rules.

Structure of ``rules.cfg``:

.. code:: ini

    # at least one pattern is required
    [patterns]
    GithubUser1=
        title:network
        text:protocol
        label:^(network|networking)$
        any:http[s]{0,1}://localhost:[0-9]{2,5}
    GithubUser2=any:Python

    # optional
    [fallback]
    label=Need assignment
