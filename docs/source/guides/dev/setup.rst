Setup
========

Local Setup
-----------

1. Fork and clone the repo

    .. code-block:: bash

        git clone https://github.com/[username]/Catherine-Chan.git && cd Catherine-Chan
    

    Or if you have the `gh` cli tool installed:

    .. code-block:: bash

        gh repo clone [username]/Catherine-Chan && cd Catherine-Chan
    

2. Install all of the dependencies (including dev dependencies)

    .. code-block:: bash

        poetry install

3. Copy the ENV files into the correct places

    .. code-block:: bash

        cp envs/dev.env bot/.env

4. Edit the ``.env`` file placed in the root of the repo and in the ``bot`` folder to include any credentials needed for the bot to run
    
    .. code-block:: bash
        
        # THIS IS ONLY AN EXAMPLE
        POSTGRES_PASSWORD=...
        POSTGRES_USER=...
        POSTGRES_URI=postgres://user:somepass@localhost:5432/somedb
        

5. Start the Docker Compose stack

    .. code-block:: bash

        sudo docker compose -f docker-compose-dev.yml up -d
    

6. Enable the PostgreSQL extension ``pg_trgm``

    .. code-block:: sql

        CREATE EXTENSION pg_trgm;

7. Run the database migrations

    .. code-block:: bash

        python migrations-runner.py

Environment Variables
---------------------

Catherine includes an development mode feature, which will set up jishaku and a custom FS watcher. The FS (File System) watcher is just like HMR (Hot Module Replacements). Once you press Ctrl+s in your cog, it will automatically reload it so the code executed is changed. Later on, there may be more development features that will be included. Make sure you first install the dev dependencies first! And in order to enable it, set an environment variable called ``DEV_MODE`` to ``True``.