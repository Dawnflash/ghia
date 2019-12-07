Code examples
=============

The following section illustrates the core inner logic.
The examples show issue processing on the code level.

.. testsetup::

    import re
    from ghia.cli import batch_process
    from ghia.github import check_match, print_assign_diff, process_issue

    config = {}
    config['strategy'] = 'append'
    config['github'] = {'token': ''}
    config['dry_run'] = True
    config['fallback'] = {'label': 'Need assignment'}

    config['patterns'] = {
        'John': [
            ('title', re.compile('^Python'))
        ],
        'Judy': [
            ('label', re.compile('[Nn]etworking'))
        ],
    }

    patterns = config['patterns']
    issues = [
        {
            'state': 'open',
            'title': 'Python rules',
            'body': '',
            'labels': [{'name': 'networking issue'}],
            'assignees': [{'login': 'Frank'}]
        },
        {
            'state': 'open',
            'title': 'python rules',
            'body': '',
            'labels': [{'name': 'Slow Networking'}],
            'assignees': []
        },
    ]
    issue1, issue2 = issues


Let's create a model situation:

``rules.cfg``:

.. code:: ini

    [patterns]
    John=title:^Python
    Judy=label:[Nn]etworking

    [fallback]
    label=Need assignment

We'll use 2 issues for demonstration:

* **issue1**: title: Python rules, label: networking issue, assignees: Frank
* **issue2**: title: python rules, label: Slow Networking, assignees: (none)

Checking for rule match
-----------------------

Check that the rules linked to the specified user match the given issue.

.. doctest::

    >>> check_match(issue1, patterns['John'])
    True
    >>> check_match(issue1, patterns['Judy'])
    True
    >>> check_match(issue2, patterns['John'])
    False

Processing single issues
------------------------

Process a single issue with the ``append`` strategy.

.. doctest::

    >>> process_issue(None, issue1, config, True)
       = Frank
       + John
       + Judy
    True

Now do it again with the ``change`` strategy. Frank should be replaced.

.. doctest::

    >>> config['strategy'] = 'change'
    >>> process_issue(None, issue1, config, True)
       - Frank
       + John
       + Judy
    True

Set strategy: populate an unassigned issue

.. doctest::

    >>> config['strategy'] = 'set'
    >>> process_issue(None, issue2, config, True)
       + Judy
    True

Set strategy: application on a populated issue does nothing

.. doctest::

    >>> process_issue(None, issue1, config, True)
       = Frank
    True
