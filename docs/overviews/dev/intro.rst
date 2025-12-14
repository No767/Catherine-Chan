Introduction
============

Catherine-Chan is internally built with discord.py. 
This document introduces relevant concepts and instructions for this project.

Prerequisites
-------------

There are some tools that you would need to have installed and prepared before you continue. 
They are listed below:

- `Git <https://git-scm.com>`_
- `Docker <https://docker.com>`_
- `Mise <https://mise.jdx.dev/installing-mise.html>`_ alongside with the environment being `activated <https://mise.jdx.dev/getting-started.html#activate-mise>`_
- Discord Account + App

If you are using Linux, the following dependencies will need to be installed:

.. tab-set::

    .. tab-item:: Debian/Ubuntu

        .. code-block:: bash

            sudo apt-get install libffi-dev libnacl-dev python3-dev libssl-dev

    .. tab-item:: Fedora

        .. code-block:: bash

            sudo dnf install libffi-devel nacl-devel python3-devel openssl-devel

    .. tab-item:: OpenSUSE

        .. code-block:: bash

            sudo zypper in libffi-devel libsodium-devel python3-devel libopenssl-devel

    .. tab-item:: Arch

        .. code-block:: bash

            sudo pacman -S libffi libsodium python3 openssl

.. _database-setup:

Database Setup
--------------

The database used is PostgreSQL By default, a Docker Compose file is included for spinning up these for development. Setup instructions are as follows:

Step 1 - Fork and clone the repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once these tools are installed, fork and clone the repository. This can be done as shown below:

::

    git clone https://github.com/SomeUser/Catherine-Chan


Step 2 - Copy ``.env`` and ``.config.dist.yml`` template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Copy ``env.dist`` to ``.env``  and ``.config.dist.yml`` to ``config.yml`` and within the root of the repository

.. tab-set::

    .. tab-item:: \*nix and MacOS

        .. code-block:: bash

            cp .env.dist .env && cp .config.dist.yml config.yml

    .. tab-item:: Windows

        .. code-block:: powershell

            copy .env.dist .env
            copy .config.dist.yml config.yml

Step 3 - Modify ``.env`` template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open up ``.env`` and modify these entries:

- ``DB_PASSWORD``: Replace the value ``password`` with a random secure password of your choice

Step 4 - Run the Docker Compose stack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. NOTE::

    On \*nix platforms, ``docker`` must be executed with root privileges through ``sudo``, as the Docker daemon binds to a Unix socket ran by the `root` user. 
    See `Manage Docker as a non-root user <https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user>`_ for further details

Now, all you need to do is to execute this command within the root directory in the repository to spin up the database:

.. tab-set::

    .. tab-item:: \*nix and MacOS

        .. code-block:: bash

            docker compose -f docker/docker-compose.dev.yml --env-file .env up -d

    .. tab-item:: Windows

        .. code-block:: powershell

            docker compose -f docker\docker-compose.dev.yml --env-file .env up -d


To bring it down, run the command as shown below:

.. tab-set::

    .. tab-item:: \*nix and MacOS

        .. code-block:: bash

            docker compose -f docker/docker-compose.dev.yml stop

    .. tab-item:: Windows

        .. code-block:: powershell

            docker compose -f docker\docker-compose.dev.yml stop

.. TIP::

    For convenience, ``mise run bot:docker:up`` and ``mise run bot:docker:stop`` can be utilized instead

Step 5 - Connect to the database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to verify that our configurations work, we can access the database through a CLI tool such as ``psql``

For example, this is the required URI to utilize for PostgreSQL. Replace ``<password>``` with your configured password:

.. code-block:: bash

    postgresql://postgres:<password>@localhost:5432/catherine


Development Setup
-----------------

.. important::
  
    You must have PostgreSQL running through Docker before setting up on your local machine. Ensure that you have completed the steps in :ref:`database-setup` before proceeding further

Step 1 - Clone the repository if needed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once these tools are installed, fork and clone the repository (if you haven't done so previously). This can be done as shown below:

::

    git clone https://github.com/SomeUser/Catherine-Chan

Step 2 - Copy ``.env`` and ``.config.dist.yml`` template if needed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Copy ``env.dist`` to ``.env``  and ``.config.dist.yml`` to ``config.yml`` and within the root of the repository (if you haven't done so previously)

.. tab-set::

    .. tab-item:: \*nix and MacOS

        .. code-block:: bash

            cp .env.dist .env && cp .config.dist.yml config.yml

    .. tab-item:: Windows

        .. code-block:: powershell

            copy .env.dist .env
            copy .config.dist.yml config.yml

Step 3 - Modify ``.env`` template if needed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open up ``.env`` and modify these entries:

- ``DB_PASSWORD``: Replace the value ``password`` with a random secure password of your choice

Step 4 - Modify ``config.yml`` template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open up ``config.yml`` and modify these entries:

- ``token``: See `Creating a Bot Account <https://discordpy.readthedocs.io/en/stable/discord.html#creating-a-bot-account>`_ for instructions to obtaining the token. Once completed, paste the token into the ``token`` entry

- ``approval_channel_id``: Hover over the channel of choice, right-click, and click the "Copy Channel ID" button. Copy this ID into the entry. Make sure that your developer bot can read and write to this channel

- ``postgres_uri``: Replace the value ``<password>`` with a random secure password of your choice


Step 5 - Create and activate the virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A virtual environment (usually shorten to venv) is a separate Python environment that is decoupled from the global environment, and helps isolate Python installs and their packages. Create and activate it as shown below:

.. tab-set::

    .. tab-item:: \*nix and MacOS

        .. code-block:: bash

            uv venv && source .venv/bin/activate

    .. tab-item:: Windows

        .. code-block:: powershell

            uv venv
            .venv\Scripts\activate.bat

Step 6 - Install development dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using `uv <https://docs.astral.sh/uv>`_, install the dependencies as shown below:

::

    uv pip install --upgrade -r requirements-dev.txt

Alternatively, ``mise run bot:install:dev`` can be used for convenience instead

Step 7 - Apply SQL schema
^^^^^^^^^^^^^^^^^^^^^^^^^

Currently, the database is empty. It doesn't have the schema, or the blueprint on how to store data. Using `Atlas <https://atlasgo.io/>`_, our schema is declared through a master schema (found in ``src/schema.sql``) and  Atlas compares the differences between the current database state and the master schema, and generates and executes a migration plan to get it to the desired state.
But first, apply the schema to the database, which is done as shown below (replace ``<password>`` with your configured PostgreSQL password):

::

    atlas schema apply --auto-approve --env local --var url="postgresql://postgres:<password>@localhost:5432/catherine?sslmode=disable&search_path=public"

Step 8 - Start the application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Afterwards, prepare a testing server, invite your development bot, and start the bot to verify that it works.

::

    mise run bot:dev

Details
-------

Documentation development
^^^^^^^^^^^^^^^^^^^^^^^^^

The same documentation that you are reading also needs to be managed. In order to edit, run ``mise run docs:auto:build`` to have the docs automatically rebuild and serve a live website hosting the documentation at `127.0.0.1 <http://127.0.0.1:8000>`_.
In order to build the documentation (usually for previewing or hosting), run ``mise run docs:preview:build`` to build. Built HTML files can be found within ``docs/_build/dist/html``.

Changes and Changelogs
^^^^^^^^^^^^^^^^^^^^^^

Changes are logged through `Towncrier <https://towncrier.readthedocs.io/en/stable/index.html>`_, and each news fragment is located under ``changes``. The format of the filename for each news fragment is ``{PR Number}.{type}.md``.
In order to document a news fragment, run the command shown below, while replacing ``<filename>`` being the filename used for the news fragment discussed previously, and ``<entry>`` being the news fragment content.

::

    mise run bot:towncrier:create --filename <filename> --entry <entry content>

In order to build the final changelog, ``mise run bot:towncrier:build`` can be utilized

Development Features
^^^^^^^^^^^^^^^^^^^^

Catherine-Chan includes an development mode allowing for continuous reloading of extensions and utils code. Once the file is saved, the module is reloaded and changes can be reflected. 
This can be enabled through the ``dev_mode`` key in ``config.yml``. In addition, Jishaku is bundled with the bot, allowing for easy debugging and faster development.

Prometheus Metrics
^^^^^^^^^^^^^^^^^^

Catherine-Chan also includes an Prometheus endpoint for metrics. This can enabled through the ``prometheus.enabled`` key. If  you don't need this feature, feel free to entirely disable it.
Disabling this feature does not affect the bot, as the cog responsible for this feature is an extension that can be enabled at will.

Type Hinting
^^^^^^^^^^^^

Catherine-Chan actively uses `type hinting <https://docs.python.org/3/library/typing.html>`_ in order to verify for types before runtime. `Pyright <https://github.com/microsoft/pyright>`_ is used to enforce this standard. Checks happen before you commit, and on Github actions.
These checks are activated by default on VSCode. Pyright is available as a LSP on Neovim.