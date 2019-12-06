Usage
#####

GHIA may be used in two modes of operation:

* CLI batch script
* Flask-powered online webhook

CLI
---

Process all issues in a given repo, batch style.

You can put your whole configuration in a single file.
In that case, point ``-a`` and ``-r`` switches to the same file.

Run the following for help:

.. code:: bash

    $ python -m ghia --help

A CLI example:

.. code:: bash

    $ python -m ghia -a auth.cfg -r rules.cfg -s set myuser/myrepo

.. _usage_webhook:

Webhook
-------

Run a Flask server receiving GitHub issue webhooks.
You can read more about GitHub webhooks `here <https://developer.github.com/webhooks/>`_.

You will need to set up a webhook sensitive to issue events.
Follow `this <https://developer.github.com/webhooks/creating/>`_ to create your own webhook.
In the process GitHub will ask you to provide an optional secret which makes the webhook communication more secure.
If you decide to use one, set it in the auth config. Refer to :ref:`github_access` for details.

In short, a server will spawn, listening for webhooks from GitHub.
Issue-related webhooks are processed in real time.

As a result, your assignment logic may execute whenever issues change!

Run the server like this:

.. code:: bash

    $ GHIA_CONFIG=<path_a, path_b, ...> FLASK_APP=ghia flask run

The configuration may reside in any number of files, make sure to refer to all of them as shown above.
The server accepts extra configuration as envvars:

* GHIA_DRYRUN: set to 1 to run dry (not commit anything to GitHub)
* GHIA_STRATEGY: use a different strategy (see :ref:`assignment_strategy` for reference)

