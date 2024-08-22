Setup
========

Local Setup
-----------

**Catherine-Chan only supports Python 3.9 or higher**

.. important::
  
  Ensure that you are in the root of the repo throughout this process and have the database running

1. Fork and clone the repo

2. Create an virtualenv

.. code-block:: bash

   python3 -m venv catherine-chan

3. Activate the virtualenv

.. code-block:: bash
  
  # Linux/MacOS
  $ source catherine-chan/bin/activate

  # Windows
  $ catherine-chan/Scripts/activate.bat

4. Install dependencies and set up pre-commit hooks

.. code-block:: bash

   pip install -r requirements-dev.txt \
   && pre-commit install

5. Copy over the ``config-example.yml`` template over to the ``bot`` directory. Modify the values as appropriate.

.. code-block:: bash

    cp config-example.yml bot/config.yml

6. Run the SQL migrations

.. code-block:: bash

    python3 bot/migrations.py init

7. In order to demonstrate, you can run the bot to test everything out

.. code-block:: bash

    python3 bot/catherinebot.py

Database
--------
    
The following SQL queries can be used to create the user and database:

.. code-block:: sql

    CREATE ROLE catherine WITH LOGIN PASSWORD 'somepass';
    CREATE DATABASE catherine OWNER catherine;
    CREATE EXTENSION IF NOT EXISTS pg_trgm;

.. note::
    
    This step is largely skipped if you are using Docker to run
    the PostgreSQL server. If you decide not to use Docker, you 
    will need to manually create the database as shown below

Using Docker
^^^^^^^^^^^^

If you decide to use Docker to run the local PostgreSQL server, then a
pre-built Docker Compose file is provided. Setup instructions are as follows:

1. Copy ``docker/example.env`` to ``.env`` within the ``docker`` folder. Modify as appropriate.

.. code-block:: bash

    cp docker/example.env docker/.env

2. Run the following command to start the PostgreSQL server

.. code-block:: bash

    docker compose -f docker/docker-compose.dev.yml up -d


Special Configuration Variables
-------------------------------

Development Features
^^^^^^^^^^^^^^^^^^^^

Catherine-Chan includes an development mode allowing for continuous
reloading of extensions and library code. Once the file is saved, the 
module is reloaded and changes can be reflected. This can be enabled 
through the ``bot.dev_mode`` key in the configuration file. In addition,
Jishaku is bundled with the bot, allowing for easy debugging and
faster development.

.. note::

    You may need to restart the bot entirely for
    some changes to be reflected.

Prometheus Metrics
^^^^^^^^^^^^^^^^^^

Catherine-Chan also includes an Prometheus endpoint for metrics.
This can enabled through the ``bot.prometheus.enabled`` key. If 
you don't need this feature, feel free to entirely disable it.
Disabling this feature does not affect the bot, as the cog
responsible for this feature is an extension that can be
enabled at will. 