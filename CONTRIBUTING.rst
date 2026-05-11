============================
Contributing to This Project
============================

Purpose
-------

This document defines the rules and expectations for contributing to this project.
Participation in contributions, including but not limited to issues, pull requests,
documentation, or other code submissions, constitutes acceptance of these terms.

Contributions are voluntary and made at the contributor's own risk.
The maintainers reserve exclusive authority over all contributions.

Project Philosophy
------------------

This project values:

* Code clarity over cleverness.
* Strong typing and static analysis.
* High test coverage.
* Explicit over implicit behavior.

Quick Start
-----------

1. Fork the repository.
2. Clone your fork locally.
3. Open the project in VS Code using Dev Containers.
4. Install pre-commit hooks:

   .. code-block:: sh

       pre-commit install

5. Create a branch from ``test``.
6. Make your changes and add tests.
7. Run:

   .. code-block:: sh

       nox -t test

8. Open a pull request targeting ``test``.

CI Status
---------

All pull requests must pass the automated CI checks before review.

General Guidelines
------------------

All contributions must:

* Follow the coding, formatting, and documentation standards defined in the project.
* Be submitted in accordance with the branching and pull request process, if applicable.
* Be relevant, constructive, and in good faith.

Submissions that do not meet these criteria may be rejected without explanation.

Scope of Contributions
----------------------

The maintainers reserve the right to:

* Accept, reject, or modify contributions at their sole discretion.
* Define which versions or branches are supported for contributions.
* Disregard contributions that are outside the intended scope or violate security or conduct policies.

No commitment is made to merge contributions, respond to submissions, or provide ongoing support.

No Compensation or Liability
----------------------------

Contributors acknowledge and agree that:

* No compensation or credit is guaranteed beyond attribution in commits or documentation.
* All contributions are provided **“as is”**.
* Maintainers and the developer disclaim all liability for any damages, losses, or consequences
  arising from submitted contributions.

Development Environment
-----------------------

Use `VS Code`_ `Dev Containers`_ extension and clone this repository.

Requirements will be installed automatically

Poetry_ manages virtual environments and dependencies for this project.

pre-commit_ manages linters, static analysis, and other tools for this project.

Install pre-commit_ hooks after cloning, run:

.. code-block:: sh

    pre-commit install

Using pre-commit_ ensures PRs match the linting requirements of the codebase.

Possible issues
---------------

If you encounter an error about not setting :code:`user.name` and :code:`user.email` for committing with git:

* Run the following commands on your **local machine** terminal to set-up your git connection

.. code-block:: sh

    git config --global user.name "YOUR_USER_NAME"

    git config --global user.email "YOUR_EMAIL"


* Rebuild the container

If you encounter an error about not having the permission to .git/object for committing with git:
:code:`insufficient permission for adding an object to repository database .git/objects`

* Run the following commands on dev container terminal:

.. code-block:: sh

    sudo chmod -R a+rwX .

    sudo find . -type d -exec chmod g+s '{}' +

* Check the output of shared repository:

.. code-block:: sh

    git config core.sharedRepository

* If the output of last command is empty or doesn't include :code:`group` , :code:`true` or :code:`1`, run the following:

.. code-block:: sh

    git config core.sharedRepository group

* Finally, fix the root cause by following the answer from stackoverflow_.

Documenting Code
----------------

Whenever possible, please add docstrings to your code.

This project follows the `google-style docstrings`_ format.

To confirm docstrings are valid, build the docs by running :code:`nox -t docs`

Good docstrings include information like:

* If the intended use-case doesn't appear clear, what purpose does this function serve? When should someone use it?
* What happens during errors/edge-cases.
* When dealing with physical values, include units.

Testing
-------

The pytest_ framework provides unit testing for this project.

Ideally, all new code is paired with new unit tests to exercise that code.

If fixing a bug, consider writing the test first to confirm the existence of the bug, and to confirm that the new code fixes it.

Unit tests should only test a single concise body of code.

Run the full test suite:

.. code-block:: sh

    nox -t test

Lint using Ruff_:

.. code-block:: sh

    nox -t fix

Typecheck using MyPy_:

.. code-block:: sh

    nox -t type

Build and live-preview documentation:

.. code-block:: sh

    nox -t preview

Run pre-commit_ hooks:

.. code-block:: sh

    nox -t pre-commit

List the available Nox_ sessions:

.. code-block:: sh

    nox --list

Unit tests are located in the *tests* directory,
and are written using the pytest_ testing framework.

Coding style
------------

In an attempt to keep consistency and maintainability in the code-base,
here are some high-level guidelines for code that might not be enforced by linters:

* Use f-strings.
* Keep/cast path variables as :code:`pathlib.Path` objects. Don't use :code:`os.path`.
  For public-facing functions, cast path arguments immediately to :code:`Path`.
* Avoid deeply nested code. Techniques like returning early and breaking up a complicated function into smaller functions results in easier-to-read and test code.
* Consider if you are double-name-spacing and how modules are meant to be imported.
  for example, it might be better to name a function :code:`read` instead of :code:`image_read` in the module :code:`my_package/image.py`.
  Consider the module name-space and check if it's flattened in :code:`__init__.py`.

Commit Messages
---------------

Use clear, descriptive commit messages.

Format:

    type(scope): short description

Examples:

* feat(ui): add mission filter dropdown
* fix(api): handle timeout exception
* docs: clarify setup instructions

..
    Links
.. _pytest: https://docs.pytest.org/en/stable/
.. _Nox: https://nox.thea.codes/en/stable/index.html
.. _pre-commit: https://pre-commit.com/
.. _MyPy: https://www.mypy-lang.org/
.. _Ruff: https://docs.astral.sh/ruff/
.. _google-style docstrings: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/#google-vs-numpy
.. _stackoverflow: https://stackoverflow.com/questions/6448242/git-push-error-insufficient-permission-for-adding-an-object-to-repository-datab/6448326#6448326
.. _Poetry: https://python-poetry.org/
.. _VS Code: https://code.visualstudio.com/
.. _Dev Containers : https://containers.dev/
