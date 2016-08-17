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

        pip install ./gossip-0.0.1.tar.gz

#. See Usage for more!


Usage
###################

Run gossip
___________________

* To start a new gossip instance on your machine, you first need to create a new directory called config at the same level of your python script.
* Second, you need to add at least two files to that directory. The first file, called logging_config.ini is needed to specify the log level of this gossip instance

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


* Third, create a file called config.ini :

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

* Once you created these files you can create a python script like this to run your gossip instance

.. code-block:: python

    from gossip.gossip_main import main as run_gossip

    if __name__ == "__main__":
        run_gossip()


Run simulation
___________________

  The simulation script generates a network based on the same algorithms that are used in gossip-python.
  This can especially useful if you want to see how the network behaves using different configuration paremeters.
  Note that you need to install the following requirements yourself to get the simulation running:
    .. code-block:: sh

        pip install networkx
        pip install matplotlib

  To run the simulation, which creates a network diagram, see following code.

.. code-block:: python

    from examples.connections_simulation import Simulation

    if __name__ == "__main__":
        sim = Simulation(number_clients=30, number_connections_per_client=5)
        sim.run()