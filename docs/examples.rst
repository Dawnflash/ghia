Code examples
=============

.. testsetup::

    import re
    from ghia.cli import batch_process
    from ghia.github import check_match, print_assign_diff, process_issue

    config = {}
    config['dry_run'] = True
    config['fallback'] = {'label': 'Need assignment'}

    config['patterns'] = {
        'John': [
            ('title', re.compile('Python'))
        ]
    }

    issues = [
        {
            'title': 'Python rules',
            'body': '',
            'name': '',
            'labels': []
        }
    ]


* cli:batch_process
* github:check_match
* github:print_assign_diff
* github:process_issue

Checking for rule match
-----------------------

.. doctest::

    >>> check_match(issues[0], config['patterns']['John'])
    True
