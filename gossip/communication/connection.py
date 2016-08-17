# Copyright 2016 Anselm Binninger, Thomas Maier, Ralph Schaumann
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import random
from multiprocessing import Manager, Lock
from socket import SHUT_RDWR
from gossip.util.exceptions import GossipIdentifierNotFound

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class GossipConnectionPool:
    """ Thread-safe implementation of a pool for Gossip connections. """
    CONNECTION = 'Connection'
    SERVER_IDENTIFIER = 'ServerIdentifier'

    def __init__(self, connection_pool_label, cache_size=30):
        """ Constructor.

        :param connection_pool_label: A label to derive the concrete functionality of this connection pool
        :param cache_size: (optional): The max. amount of connections in this connection pool.
        """
        self.connection_pool_label = connection_pool_label
        self._connections = Manager().dict()
        self._cache_size = cache_size
        self._pool_lock = Lock()

    def add_connection(self, identifier, connection, server_identifier=None):
        """ Adds new identifier with its connection.

        :param identifier: An object which identifies an unique connection
        :param connection: A connection object
        :param server_identifier: (optional) The server identifier of the peer
        """
        self._pool_lock.acquire()
        if identifier not in self._connections:
            self._connections[identifier] = {GossipConnectionPool.CONNECTION: connection,
                                             GossipConnectionPool.SERVER_IDENTIFIER: server_identifier}
            logging.debug('%s | Added new connection %s (pool: %s)' % (self.connection_pool_label, identifier, self))
            self._pool_lock.release()
            self.__maintain_connections()
        else:
            self._pool_lock.release()
            logging.debug('%s | Connection %s exists already (pool: %s)' % (self.connection_pool_label, identifier,
                                                                            self))

    def update_connection(self, identifier, server_identifier):
        """ Updates an existing identifier with its connection.

        :param identifier: An object which identifies an unique connection
        :param server_identifier: The server identifier of the peer
        """
        self._pool_lock.acquire()
        if identifier in self._connections:
            connection_to_update = self._connections[identifier][GossipConnectionPool.CONNECTION]
            self._connections[identifier] = {GossipConnectionPool.CONNECTION: connection_to_update,
                                             GossipConnectionPool.SERVER_IDENTIFIER: server_identifier}
            logging.debug('%s | Updated information about connection %s (pool: %s)' % (self.connection_pool_label,
                                                                                       identifier, self))
        else:
            logging.debug('%s | Updating information about connection %s failed because it does not exist anymore'
                          % (self.connection_pool_label, identifier))
        self._pool_lock.release()

    def remove_connection(self, identifier):
        """ Removes an existing connection from the pool.

        :param identifier: Unique identifier to find the affected connection
        """
        self._pool_lock.acquire()
        removed_connection = self._connections.pop(identifier, None)
        if removed_connection:
            logging.debug('%s | Removed connection %s (pool: %s)' % (self.connection_pool_label, identifier, self))
            self._pool_lock.release()
            return removed_connection[GossipConnectionPool.CONNECTION]
        self._pool_lock.release()

    def get_connection(self, identifier):
        """ Gets a connection from the pool.

        :param identifier: Unique identifier to find the affected connection
        """
        self._pool_lock.acquire()
        connection = self._connections.get(identifier, None)
        if connection:
            self._pool_lock.release()
            return connection[GossipConnectionPool.CONNECTION]
        else:
            self._pool_lock.release()
            raise GossipIdentifierNotFound('Cannot find identifier %s' % identifier)

    def get_server_identifier(self, identifier):
        """ Gets the server identifier for one connection.

        :param identifier: Unique identifier to find the affected server identifier
        """
        self._pool_lock.acquire()
        connection = self._connections.get(identifier, None)
        if connection:
            self._pool_lock.release()
            return connection[GossipConnectionPool.SERVER_IDENTIFIER]
        else:
            self._pool_lock.release()
            raise GossipIdentifierNotFound('Cannot find identifier %s' % identifier)

    def get_identifiers(self):
        """ Gets a list of all identifiers.

        :returns: List of all identifier strings
        """
        self._pool_lock.acquire()
        identifiers = self._connections.keys()
        self._pool_lock.release()
        return identifiers

    def get_server_identifiers(self, identifier_to_exclude=None):
        """ Collects server identifiers

        :param identifier_to_exclude: (optional) Server identifiers to exclude
        """
        if not identifier_to_exclude:
            identifier_to_exclude = []

        server_identifiers = []
        self._pool_lock.acquire()
        for identifier, connection in self._connections.items():
            server_address = connection[GossipConnectionPool.SERVER_IDENTIFIER]
            if server_address and server_address not in identifier_to_exclude:
                server_identifiers.append(server_address)
        self._pool_lock.release()
        return server_identifiers

    def __str__(self):
        output = ', '.join(['%s<=%s' % (key, val[GossipConnectionPool.SERVER_IDENTIFIER])
                            for key, val in self._connections.items()])
        if output == '':
            output = 'Pool is empty'
        return output

    def __maintain_connections(self):
        """ Maintains the list of connections. If number of current connections exceeds maximum cache size a random
        connection is killed. """
        if len(self._connections) > self._cache_size:
            self._pool_lock.acquire()
            connection_to_remove = list(self._connections.keys())[random.randint(0, len(self._connections) - 1)]
            self._pool_lock.release()
            killed_connection = self.remove_connection(connection_to_remove)
            killed_connection.shutdown(SHUT_RDWR)
            killed_connection.close()
            logging.debug('%s | Connection maintainer removes: %s (current pool: %s)' % (self.connection_pool_label,
                                                                                         connection_to_remove, self))

    def get_capacity(self):
        """ Provides the left capacity of the current connection pool.

        :returns: The left capacity
        """
        return self._cache_size - len(self._connections)

    def filter_new_server_identifiers(self, server_identifiers, identifier_to_exclude=None):
        """ Provides all given identifiers which are not known until now.

        :param server_identifiers: Server identifiers to check against known ones
        :param identifier_to_exclude: (optional) Server identifiers to exclude
        :returns: Identifiers which are not known as server identifiers in the connection pool until now
        """
        known_server_identifiers = self.get_server_identifiers(identifier_to_exclude=identifier_to_exclude)
        new_identifiers = []
        for server_identifier in server_identifiers:
            if server_identifier not in known_server_identifiers:
                new_identifiers.append(server_identifier)
        return new_identifiers

    def get_random_identifier(self, identifier_to_exclude):
        """ Provides a random identifier which represents an active connection in the pool at the moment.

        :param identifier_to_exclude: Identifier to exclude
        :returns: Random identifier
        """
        self._pool_lock.acquire()
        identifiers = [identifier for identifier in self._connections.keys() if identifier != identifier_to_exclude]
        self._pool_lock.release()
        if len(identifiers) > 1:
            return identifiers[random.randint(0, len(identifiers) - 1)]
        elif len(identifiers) == 1:
            return identifiers[0]
        else:
            return None
