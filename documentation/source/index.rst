.. gossip documentation master file, created by
   sphinx-quickstart on Wed Apr 27 19:34:41 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to gossip's documentation!
==================================

Contents:

.. toctree::
   :maxdepth: 2
   .. automodule:: gossip
      gossip
      :maxdepth: 2


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Getting Started
==================

Other
##################


#. You can download this documentation file from: `gossip-python.pdf <gossip-python.pdf>`_
#. The current pylint output can be found here `pylint-gossip <pylint.html>`_
#. The current test outputs can be found here `gossip-test ouput <test_output.html>`_

Installation
###################

#. Download gossip from  `Downloads <https://bwk-software.com/builds/gossip/downloads/>`_
#. Install gossip
    .. code-block:: sh

        # From pypi
        pip install gossip-python
        
        # Latest from github
        pip install git+https://github.com/thomai/gossip-python.git

        # Install for development from cloned repos
        pip install -e .

        # Several optional dependencies are also available
        pip install -e .[test] # Pytest support
        pip install -e .[doc] # Sphinx build support
        pip install -e .[sim] # Simulation support
        pip install -e .[sim,doc,test] # Full dev kit

#. See Usage for more!


Usage
###################

Creating configuration files
___________________

    Gossip configurations can be stored in 3 different locations:

    * ``[PROJECT DIRECTORY]/config/config.ini``
    * ``~/.config/gossip/config.ini``
    * ``~/.gossip/config.ini``

    The later two are cross platform where ``~`` maps to ``/home/username`` in POSIX systems
    or ``%USERPROFILE%`` in Windows. The configuration file can be explicitly specified by
    setting the GOSSIP_CONFIG environment variable. Next create the following two configuration
    files in one of the above search paths. If they are not created a template will be created
    in ``~/.gossip/[CONFIG_FILE_NAME]``:

**logger_config.ini**

.. code-block:: ini

    [loggers]
    keys=root

    [handlers]
    keys=consoleHandler

    [formatters]
    keys=simpleFormatter

    [logger_root]
    level=DEBUG
    handlers=consoleHandler

    [handler_consoleHandler]
    class=StreamHandler
    level=DEBUG   # Replace this with the log level you want, for production we recommend ERROR
    formatter=simpleFormatter
    args=(sys.stdout,)

    [formatter_simpleFormatter]
    format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
    datefmt=%d.%m.%Y %H:%M:%S


**config.ini**

.. code-block:: ini

    [GOSSIP]
    # Max number of messages this peer can cache
    cache_size = 50
    # Max number of peer connections this peer can hold
    max_connections = 30
    # The bootstrapping gossip instance (leave empty if you want to act as the bootstrapper)
    bootstrapper = 192.168.1.100:6001
    # The address this machine listens for peer connections
    listen_address = 192.168.1.99:6001
    # The address this machine listens for api connections
    api_address = 192.168.2.99:7001
    # Used for messages that are sent through the api
    max_ttl = 0

Note that you should replace the listen_address and api_address with the ip address of your machine.
If you want your machine to be the bootstrapping machine, leave bootstrapper empty. If not replace this with
the list_address of the machine you want to use as the bootstrapper. eg (192.168.1.100:6001)
For an example of a api application see this repository: `ChatNow! - Repository <https://stash.bwk-technik.de/projects/PTP/repos/p2p-api-client/browse>`_
If you want to test your gossip network you can download the latest ChatNow!
Client from `ChatNow! - Downloads <https://bwk-software.com/builds/gossip-ui/>`_

Run gossip
___________________

    Gossip can be run in two ways after configuration.

    * Entrypoint
        .. code-block:: sh

            gossip

    * Python Module Execution
        .. code-block:: sh

            python -m gossip

Run examples
___________________


    Examples are populated via the scripts convention in setup.py. The following
    example scripts are available:

    * gossip_connections_simulation.py
    * gossip_peer_request_response.py
    * gossip_receive_test.py
    * gossip_send_test.py

Simulation
^^^^^^^^^^

  The simulation script generates a network based on the same algorithms that are used in gossip-python.
  This can especially useful if you want to see how the network behaves using different configuration paremeters.
  Note that you need to install the following requirements yourself to get the simulation running:

    .. code-block:: sh

        pip install gossip-python[sim]

  To run the simulation, simply execute it by calling the 

    .. code-block:: sh

        gossip_connections_simulation.py

Send and Receive Test
^^^^^^^^^^^^^^^^^^^^^

    To run a simple send/receive test do the following

    .. code-block:: sh

        gossip &
        GOSSIP_PID=$!
        gossip_receive_test.py &
        gossip_send_test
        # Send and receive tests will now connect to each other...

        # When they're done executing cleanup the gossip instance
        kill -9 $GOSSIP_PID

Peer Request Response
^^^^^^^^^^^^^^^^^^^^^

    To run a simple send/receive test do the following

    .. code-block:: sh
        
        gossip &
        GOSSIP_PID=$!
        gossip_peer_request_response.py
        # When done executing cleanup the gossip instance
        kill -9 $GOSSIP_PID

Development with Docker
_______________________

    To make it easy to develop rapidly a Dockerfile has been created and can
    be build-run using the following command:

Build Standard
^^^^^^^^^^^^^^

    This builds a docker container with gossip installed and a man-page generated.

    .. code-block:: sh

        docker build -t gossip:latest .
        docker run --rm -it \ # Run interactive but get rid of container after
            -v /path/to/config/dir:/root/.gossip \ # (Optional) Mount local configurations to container
            -p6001:6001 -p7001:7001 \ # Forward ports
            gossip:latest
        root@ec6c0e56f101:/app# man gossip-python
        # Displays man-page
        root@ec6c0e56f101:/app# gossip & # Run the server
        root@ec6c0e56f101:/app# gossip_connections_simulation.py # Run an example


Build Slim
^^^^^^^^^^

    To build with only the bare minimum requirements (no documentation, test or 
    simulation dependencies), specify an empty argument for optional_deps:

    .. code-block:: sh

        docker build --build-arg optional_deps= -t gossip:latest 
        docker run --rm -it -p6001:6001 -p7001:7001 gossip:latest

Recommended Development Build
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    For testing it's recommended to install all dependencies:

    .. code-block:: sh

        docker build --build-arg optional_deps=[test,doc,sim] -t gossip:latest .

        # Run development docker container, will drop to a bash shell
        docker run --rm -it -p6001:6001 -p7001:7001 gossip:latest /bin/bash

        # Run tests and exit
        docker run --rm -it gossip:latest pytest

        # Just run the gossip_connections_simulation.py and launch a webserver to view the pdf
        docker run --rm -it -p8000:8000 gossip:latest bash -c "gossip_connections_simulation.py && python -m http.server"
        # You can then view the pdf at http://localhost:8000/path_graph.pdf

    You can also do one-time builds of the documentation to view as html or pdf outputs

    .. code-block:: sh

        # Build html docs and launch a server on localhost:8000 to view them
        docker run --rm -it -p8000:8000 gossip:latest bash -c "cd documentation && make html && python -m http.server --directory build/html"

        # Build the container with texlive-base and build pdf docs and launch a server on localhost:8000 to view them
        docker build --build-arg extra_os_packages="texlive-latex-extra latexmk" -t gossip:latest .
        docker run --rm -it -p8000:8000 gossip:latest bash -c "cd documentation && make latexpdf && python -m http.server --directory build/latex"
        # Pdf is then available via http://localhost:8000/gossip-python.pdf
