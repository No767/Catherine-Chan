Setup
========

Local Setup
-----------

1. Fork and clone the repo

    .. code-block:: bash

        git clone https://github.com/[username]/Catherine-Chan.git && cd Catherine-Chan
    

    Or if you have the ``gh`` cli tool installed:

    .. code-block:: bash

        gh repo clone [username]/Catherine-Chan && cd Catherine-Chan
    

2. Create an virtualenv and activate it

    .. code-block:: bash

        python3 -m venv catherine-venv
        source catherine-venv/bin/activate

    On Windows you activate it with:

    .. code-block:: bash

        .\catherine-venv\Scripts\activate

3. Install development dependencies. This will install dev and testing dependencies

    .. code-block:: bash

        pip install -r requirements-dev.txt

4. Activate pre-commit

    .. code-block:: bash

        pre-commit install

5. Copy configuration file into the correct place. Edit these as needed

    - ``config-example.yml`` --> ``bot/config.yml``

6. Start the Docker Compose stack

    .. code-block:: bash

        sudo docker compose -f docker-compose-dev.yml up -d

7. Run the database migrations

    .. code-block:: bash

        python3 bot/migrations.py

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