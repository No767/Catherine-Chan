Contributing Guide
======================

Note to new contributors
---------------------------

When you contribute to this project, you are subject to the `Code of Conduct <https://github.com/No767/Catherine-Chan/blob/main/CODE_OF_CONDUCT.md>`_. Any violations of the Code Of Conduct will be handled as stated. Read the contributing guide. **Support is not given if you didn't bother reading the documentation for setting up any of the requirements, or if you didn't bother to read the contributing guide.**

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

For the most part, Catherine-Chan's codebase is fully typed. Pyright in this case is used to check whether the code is typed and meets standards or not. If you are using VS Code, then you can enable this on VSC by clicking on the ``{}`` icon in your status bar.

Formatting
^^^^^^^^^^^

Catherine-Chan uses pre-commit hooks to format all of the code. The formatters used are Black, AutoFlake, and isort. Make sure run ``git add --all`` before committing to add all of the files that you wish to stage. More than likely you'll need to commit twice due to the formatting that pre-commit does afterwards.

Docstrings
^^^^^^^^^^^

Just like how major programs are documented, the libraries that are custom made for Catherine-Chan also have to be documented. The current standard for this project is to use `Google's Docstring Guide <https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings>`_. A handy VS Code extension that should be used is the `autoDocstring <https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring>`_ extension. By default it will generate the docstring in the Google format. Docstrings should be used on all coroutines and methods (excluding cogs), and on classes as well (for classes, do not include the args). 

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

Catherine-Chan's codebase is written to keep compatibility for Python versions 3.8 - 3.11. Generally speaking, a Python version is supported until it's EOL (when the security support ends).

When a new version of Python releases, support for that version cannot be added **until the next patch version of that release** or until all packages and codebase internally support that new release. This means support for Python 3.12 for example, will not be included until Python 3.12.1 releases.

When writing code for this project, you must keep in mind to ensure that your code is compatible for versions 3.8 - 3.11. If said code is not compatible, then it will not be merged.

GitHub Contributing Guidelines
-----------------------------------

Issue and Feature Requests Reports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If there is an issue or a feature you want to be added, use the built-in GitHub issue tracker. Though a system like Jira could be used, it would be more efficient to just use the issue tracker that GitHub provides. 

- If submitting a issue report, follow the template. Duplicates will not receive support
- If submitting a feature request, follow the template as well. As with issue reports, duplicate requests will not receive support

Git Commit Styleguides
^^^^^^^^^^^^^^^^^^^^^^^

- If updating any other files that aren't project files or not important (stuff like README.md, contributing.md, etc), add the [skip ci] label in the front
- With each new commit, the message should be more or less describing the changes. Please don't write useless commit messages...

Source Control Branching Models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This project uses the standard and quite old Git Flow model. The development branch is ``main``, and the production branch is ``stable``. Each commit into stable represents a version release, whether it is a small fix or a major update. **DO NOT** make PRs off of the ``stable`` branch (you probably can't), as each version update is guaranteed to be completely stable and production ready. 

Instead, you are encouraged to fork only the ``main`` branch, and make PRs off of that. Once merged, then the feature or change will be included within the latest release.

Releasing Tags
^^^^^^^^^^^^^^^

In order to automate the release system, you have to make sure that in order to use it, the git commit message must be done correctly. Only use this if there is a new update that is ready to be released. Catherine-Chan uses `SemVer <https://semver.org/>`_  as the standard for versioning. Here's a table that should help with explaining this:

 =============================================================== ===================== 
                Type of Release, Update, or Patch                       Example        
 =============================================================== ===================== 
  Major Release (For updates that are not backwards compatible)   ``v2.0.0 #major``  
    Minor Release (For updates that are backwards compatible)     ``v2.5.0 #minor``   
   Patch Release (For critical security patches and bug fixes)    ``v2.5.1 #patch``    
 =============================================================== ===================== 
