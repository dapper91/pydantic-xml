.. _contribute:


Development
~~~~~~~~~~~

Initialize the development environment installing dev dependencies:

.. code-block:: console

    $ poetry install --no-root


Code style
__________

After any code changes made make sure that the code style is followed.
To control that automatically install pre-commit hooks:

.. code-block:: console

    $ pre-commit install

They will be checking your changes for the coding conventions used in the project before any commit.


Pull Requests
_____________

The library supports both pydantic versions: `v1 <https://docs.pydantic.dev/1.10/>`_ (legacy)
and `v2 <https://docs.pydantic.dev/2.0/>`_ (latest).
Since version 1 is outdated only bugfixes and security fixes will be accepted.
New features should be targeted to version 2.

Version 1
*********

To make a PR to version 1 checkout branch ``v1`` and create a new branch implementing your changes.

Version 2
*********

To contribute to version 2 checkout branch ``dev``, create a feature branch and make a pull request setting
``dev`` as a target.


Documentation
_____________

If you've made any changes to the documentation, make sure it builds successfully.
To build the documentation follow the instructions:

- Install documentation generation dependencies:

.. code-block:: console

    $ poetry install -E docs

- Build the documentation:

.. code-block:: console

    $ cd docs
    $ make html
