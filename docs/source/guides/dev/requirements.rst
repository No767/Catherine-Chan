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

.. WARNING::
   Catherine-Chan is natively developed for Linux, and only supports Linux and MacOS.
   Due to `uvloop being not supporting Windows <https://github.com/MagicStack/uvloop/issues/14>`_,
   since `the codebase leans heavily into the Unix core w/ epolling and forking <https://github.com/MagicStack/uvloop/issues/536#issuecomment-1553968437>`_,
   the usage of Catherine-Chan on Windows is not supported.

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