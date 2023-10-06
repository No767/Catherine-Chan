Internals
==========

This page is meant to document the internals of how Catherine-Chan work from a developer's perspective.

Project Structure
-----------------


.. code-block:: text

        "."
    |-- "Makefile"
    |-- "README.md"
    |-- "assets"
    |-- "bot"
    |   |-- "catherinebot.py"
    |   |-- "catherinecore.py"
    |   |-- "cogs"
    |   |   |-- "__init__.py"
    |   `-- "libs"
    |       |-- "cog_utils"
    |       |-- "ui"
    |       `-- "utils"
    |           |-- "__init__.py"
    |           |-- "pages"
    |-- "docker"
    |-- "docs"
    |-- "envs"
    |-- "migrations"
    |-- "requirements"
    `-- "tests"


Figure 1 - The most simplified version of the project structure.

Above shown in Figure 1, is the project structure. Some folders will need to have an explanation for them. Thus here are the explanations for the folders:

* ``bot`` - The directory that contains all bot related code and files.
* ``cogs`` - The directory that contains all the cogs that the bot will load. If you don't know what a ``Cog`` is, please see `this <https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html>`_.
* ``libs`` - This directory contains sub-packages that each relate to common library code written. These are all self-written and are not external libraries.
    * ``cog_utils`` - All the utilities functions, coroutines, and others get placed here. This sub-package in turn contains sub-packages that each relate to a specific cog. For example, if I wanted to write utilities for the extension ``support.py``, then it would be placed under ``cog_utils/support``.
    * ``ui`` - All of the `UI components <https://discordpy.readthedocs.io/en/latest/interactions/api.html#bot-ui-kit>`_ of all of the cogs get placed here. The way that this sub-package is structured is exactly the same as the structure for ``cog_utils``.
    * ``utils`` - All of the utility functions, coroutines, and others that are not related to a specific cog get placed here. 
        * ``pages`` - Catherine-Chan's custom ``discord-ext-menu`` paginator and all utilities for that are located here. The paginator is a modified version of `RoboDanny's paginator <https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/paginator.py#L30C1-L233C20>`_ that is modified to work for interactions only.
* ``docker`` - Contains the Dockerfiles that can be used to build Catherine-Chan.
* ``docs`` - Contains the documentation that you are reading right now.
* ``envs`` - ENV file templates
* ``migrations`` - Contains all SQL migrations. They have to be written out like this: ``<date>_rev<num>_up_rev<num>.sql``. This project uses `asyncpg-trek <https://github.com/adriangb/asyncpg-trek>`_ as the migration handler. I'm not the one who made this library. If you want some examples, please see the `repo tests <https://github.com/adriangb/asyncpg-trek/tree/main/tests/asyncpg_revisions>`_.
* ``requirements`` - Poetry-exported requirements.txt file. These are exported by Poetry for production use. If you want to install the packages for development use, please use Poetry instead.
* ``tests`` - All unit tests go in here. These are separated by feature. 