gossip-python
=============
Documentation is available here: https://pythonhosted.org/gossip-python/

gossip-python is an implementation of the `gossip protocol <https://en.wikipedia.org/wiki/Gossip_protocol>`_
. It started as an university project for the lecture `Peer-to-Peer Systems and Security <https://www.net.in.tum.de/teaching/ss16/p2p.html>`_ at the Technical University of Munich (TUM).

The authors of gossip-python are Thomas Maier (ga85how@mytum.de), Anselm Binninger (ga85dib@mytum.de) and Ralph O. Schaumann (ga65gis@mytum.de).

Installation with pip:

 ``pip install gossip-python``


Development install with pip:

.. code-block:: sh
        # From root of the project structure
        pip install -e .[test] # Pytest support
        pip install -e .[doc] # Sphinx build support
        pip install -e .[sim] # Simulation support

Please use the `documentation <https://pythonhosted.org/gossip-python/>`_ for basic usage and examples.
