Contributing Guide
======================

Note to new contributors
---------------------------

When you contribute to this project, you are subject to the `Code of Conduct <https://github.com/No767/Catherine-Chan/blob/main/CODE_OF_CONDUCT.md>`_. 
Any violations of the Code Of Conduct will be handled as stated. Read the contributing guide. 
**Support is not given if you didn't bother reading the documentation for setting up any of the requirements, or if you didn't bother to read the contributing guide.**

Before Starting
----------------

Make suer to read these guides listed below (read them in order):

- :doc:`requirements`
- :doc:`setup`

Coding Style
-------------

.. note::

    If these standards are not met, more than likely the PR will not get merged and be rejected.

Variables
^^^^^^^^^^

Like all of my other projects, Catherine-Chan follows PEP8 naming conventions and standards.

Ruff is used to lint and check whether the code meets PEP8 standards or not. In order to learn more about PEP8, see `this <https://realpython.com/python-pep8/>`_ guide.

Static Typing (aka Type Hinting)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the most part, Catherine-Chan's codebase is fully typed. 
Pyright in this case is used to check whether the code is typed and meets standards or not. 
If you are using VS Code, then you can enable this on VSC by clicking on the ``{}`` icon in your status bar.

Formatting
^^^^^^^^^^^

Catherine-Chan uses pre-commit hooks to format all of the code. The formatters used are Black, AutoFlake, Ruff and isort.

Public Exports
^^^^^^^^^^^^^^

Catherine-Chan uses ``as`` imports to publicly denote and export functions, coroutines, and classes.
This is the same style of exporting that `Soheab uses <https://github.com/Soheab/modal-paginator/blob/main/discord/ext/modal_paginator/__init__.py>`_ (and also discord.py).
The purpose of doing this would be to avoid adding the names of the functions, coroutines, and/or classes that are exported and checked by Pyright to ``__all__``.

For example, I have the following package:

.. code-block:: text

    |-- "utils"
    |   |-- "__init__.py"
    |   |-- "views.py"

Assume that in ``views.py`` there exists a class called ``MyView`` (which is a subclass of ``discord.ui.View``).
The code (or export) in ``__init__.py`` would look like this:

.. code-block:: python

    from .views import MyView as MyView

Docstrings
^^^^^^^^^^^

Just like how major programs are documented, the libraries that are custom made for Catherine-Chan also have to be documented. 
The current standard for this project is to use `Google's Docstring Guide <https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings>`_. 
A handy VS Code extension that should be used is the `autoDocstring <https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring>`_ extension. 
By default it will generate the docstring in the Google format. Docstrings should be used on all coroutines and methods (excluding cogs),
and on classes as well (for classes, do not include the args). 

Google, Numpy, and Sphinx docstrings are also supported for commands. Catherine-Chan is documented w/ Google docstrings, so please make sure to use that format.

Example Cog:

.. code-block:: python

    import discord

    from catherinecore import Catherine
    from discord.ext import commands
    
    class MyCog(commands.Cog):
        """An example cog for demo purposes"""
        def __init__(self, bot: Catherine):
            self.bot = bot

        @app_commands.command(name="hello")
        async def my_command(self, interaction: discord.Interaction):
            """This is an example of a description for a slash command"""
            await interaction.response.send_message(f"Hello {interaction.user.name}!")

    async def setup(bot: Catherine):
        await bot.add_cog(MyCog(bot))

Python Version Support
----------------------

Catherine-Chan generally follows `NEP-29 <https://numpy.org/neps/nep-0029-deprecation_policy.html>`_. 
Catherine-Chan is tested against versions supported by NEP-29.

Unit Tests
----------

Since `PR #189 <https://github.com/No767/Catherine-Chan/pull/189>`_, unit tests are now used to ensure software
quality. Each feature PR should include unit tests on methods that are relevant to the cog, and features that
can tested if possible. Please see ``bot/tests`` for examples of how to write these tests.

GitHub Contributing Guidelines
-----------------------------------

Issue and Feature Requests Reports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If there is an issue or a feature you want to be added, it is recommended that you add the idea under ``#suggestions`` on the support server first.
You may also include the issue or feature on GitHub as well.

- If submitting a issue report, follow the template. Duplicates will not receive support
- If submitting a feature request, follow the template as well. As with issue reports, duplicate requests will not receive support

Git Commit Styleguides
^^^^^^^^^^^^^^^^^^^^^^^

- If updating any other files that aren't project files or not important (stuff like README.md, contributing.md, etc), add the [skip ci] label in the front
- With each new commit, the message should be more or less describing the changes. Please don't write useless commit messages...

Source Control Branching Models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: /_static/trunk.png
   :align: center
   :width: 800

This project uses an **trunk-based** development. The development branch is ``main``.
Each commit into ``main`` represents an known working version of the project.
You are encouraged to make PRs off of the ``main`` branch. 

Releasing Tags
^^^^^^^^^^^^^^^

In order to automate the release system, you have to make sure that in order to use it, the git commit message must be done correctly. 
Only use this if there is a new update that is ready to be released. 
Catherine-Chan uses `SemVer <https://semver.org/>`_  as the standard for versioning. Here's a table that should help with explaining this:

 =============================================================== ===================== 
                Type of Release, Update, or Patch                       Example        
 =============================================================== ===================== 
  Major Release (For updates that are not backwards compatible)   ``v2.0.0 #major``  
    Minor Release (For updates that are backwards compatible)     ``v2.5.0 #minor``   
   Patch Release (For critical security patches and bug fixes)    ``v2.5.1 #patch``    
 =============================================================== ===================== 
