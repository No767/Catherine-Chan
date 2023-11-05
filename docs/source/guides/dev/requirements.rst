Requirements
==================================


Software Requirements
---------------------
Before you get started, please ensure you have the following installed:

- `Git <https://git-scm.com>`_
- `Python 3 <https://python.org>`_
- `Poetry <https://python-poetry.org>`_
- `Docker <https://docker.com>`_
- Discord Account + App

.. NOTE::
    Catherine-Chan replaces the default event loop with `uvloop <https://github.com/MagicStack/uvloop>`_ on Linux and MacOS
    and `winloop <https://github.com/Vizonex/Winloop>`_ on Windows. Replacing the default event loop with these libraries
    is how Catherine-Chan is able to be extremely performant.
    Although Catherine-Chan is natively developed for Linux and MacOS,
    Windows support has not been tested.

Package Prerequisites
----------------------

Debian/Ubuntu
^^^^^^^^^^^^^

.. code-block:: bash

    sudo apt-get install libffi-dev python3-dev libnacl-dev libopus-dev \
    libssl-dev curl wget git make


Fedora
^^^^^^^^^^

.. code-block:: bash

    sudo dnf install make libffi-devel python3-libnacl python3.11-devel \
    openssl-devel opus-devel curl wget git

OpenSUSE
^^^^^^^^

.. code-block:: bash

    sudo zypper install make openssl-devel libffi-devel \
    python311-devel python311-libnacl wget git curl

Arch Linux
^^^^^^^^^^

.. code-block:: bash

    sudo pacman -S --needed base-devel openssl libffi python python-libnacl make

MacOS
^^^^^

.. code-block:: bash

    brew install openssl libffi git curl make