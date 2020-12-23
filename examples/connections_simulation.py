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

import random
import logging
import logging.config
import argparse
import networkx
from multiprocessing import Lock

from gossip.communication.connection import GossipConnectionPool
import matplotlib

matplotlib.use('PDF')
import matplotlib.pyplot as plt

__author__ = 'Anselm Binninger, Ralph Oliver Schaumann, Thomas Maier'

import sys


# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int)
        bar_length   - Optional  : character length of bar (Int)
    """
    filled_length = int(round(bar_length * iteration / float(total)) / 2)
    percents = round(100.00 * (iteration / float(total)), decimals)
    bar = u'\u2588' * filled_length + u'\u2591' * int(bar_length / 2 - filled_length)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')
        sys.stdout.flush()


class GossipConnectionPoolFast(GossipConnectionPool):

    def __init__(self, connection_pool_label, cache_size=30):
        """Constructor."""
        self.connection_pool_label = connection_pool_label
        self._connections = {}
        self._cache_size = cache_size
        self._pool_lock = Lock()

class Client:
    """Dummy class that mocks a client"""

    def __init__(self, ip, port, bootstrapper, max_chache_size=30):
        self.ip = ip
        self.port = port
        self.max_cache_size = max_chache_size
        self.bootstrapper = bootstrapper
        self._connection_pool = GossipConnectionPoolFast(connection_pool_label="%s:%s" % (ip, port),
                                                     cache_size=self.max_cache_size)
        self._connection_pool._connections = {}

    def get_ident(self):
        return '%s:%s' % (self.ip, self.port)

    def add_connection(self, connection):
        if connection.get_client(self).get_ident() != self.get_ident():
            self._connection_pool.add_connection(connection=connection,
                                                 identifier=connection.get_client(self).get_ident())

    def get_connection_idents(self):
        return self._connection_pool.get_identifiers()

    def get_connections(self):
        return [self._connection_pool.get_connection(ident) for ident in self._connection_pool.get_identifiers()]

    def notify(self, other_client):
        self._connection_pool.remove_connection(other_client.get_ident())
        if len(self._connection_pool.get_identifiers()) < self.max_cache_size - 1:
            logging.info("%s - Pool not full!!!!" % self.get_ident())
            other_connections = []
            connections = self.get_connections() + self.bootstrapper.get_connections() if self.bootstrapper else []
            for connection in connections:
                other_client = connection.second_client
                other_clients_connections = other_client.get_connections()
                for other_connection in other_clients_connections:
                    if other_connection.second_client.get_ident() != self.get_ident() and \
                                    len(
                                        other_connection.second_client.get_connection_idents()) < self.max_cache_size - 1:
                        other_connections.append(other_connection)
            if len(other_connections) > 0:
                random_connection = other_connections[random.randint(0, len(other_connections) - 1)]
                logging.debug("Pool not full, connection to random new client: %s",
                              random_connection.second_client.get_ident())
                new_connection = Connection(self, random_connection.second_client)
                new_connection.initiate()


class Connection:
    def __init__(self, first_client, second_client):
        self.first_client = first_client
        self.second_client = second_client

    def initiate(self):
        self.first_client.add_connection(self)
        self.second_client.add_connection(Connection(self.second_client, self.first_client))

    def close(self):
        self.first_client.notify(self.second_client)
        self.second_client.notify(self.first_client)

    def shutdown(self,param):
        pass

    def get_client(self, client):
        if client == self.second_client:
            return self.first_client
        else:
            return self.second_client

    def __str__(self):
        return "%s -> %s" % (self.first_client.get_ident(), self.second_client.get_ident())

    def __repr__(self):
        return self.__str__()


class Simulation:
    def __init__(self, number_clients=1000, number_connections_per_client=30):
        print("Running simulation with %s peers and %s connections per peer" % (
            number_clients, number_connections_per_client))
        self._number_clients = number_clients
        self._number_connections_per_client = number_connections_per_client

    def run(self):
        ip_addresses = ['192.168.1.%s' % x for x in range(1, self._number_clients + 1)]
        ports = [x for x in range(1, 2)]
        clients = []
        progress = 0
        for ip_addr in ip_addresses:
            progress += 1
            print_progress(progress, self._number_clients, suffix="Running simulation")
            for port in ports:
                client = Client(ip_addr, port, clients[0] if len(clients) > 0 else None,
                                max_chache_size=self._number_connections_per_client)
                clients.append(client)
                connection = Connection(client, clients[0])
                connection.initiate()

                bootstrapper_connections = clients[0].get_connections()
                for conn in bootstrapper_connections:
                    connection = Connection(client, conn.second_client)
                    connection.initiate()

        graph = networkx.nx.Graph()
        for client in clients:
            logging.info(client.get_ident())
            logging.info(client.get_connection_idents())
            for node in client.get_connections():
                graph.add_edge(node.first_client.get_ident(), node.second_client.get_ident())

        networkx.draw(graph, with_labels=False)
        plt.savefig("path_graph.pdf")
        print("Network is connected: %s" % networkx.is_connected(graph))
        print("Average shortest path length: %s" % networkx.average_shortest_path_length(graph))
        print("Average bipartite clustering coefficient %s" % networkx.average_clustering(graph))
        print("Bipartite clustering coefficient %s" % networkx.clustering(graph))
        print("degree_assortativity_coefficient %s" % networkx.degree_assortativity_coefficient(graph))


parser = argparse.ArgumentParser(description='Run gossip simulation')
parser.add_argument('-n', dest='peers', type=int, default=50,
                    help='Number of clients to run the simulation with')
parser.add_argument('-c', dest='connections', type=int, default=6,
                    help='Number of connections allowed per client')

if __name__ == '__main__':
    args = parser.parse_args()
    sim = Simulation(number_clients=args.peers, number_connections_per_client=args.connections)
    sim.run()
    print("\n################################################################\n")
    print("INFO: Network diagram saved to current file directory (path_graph.pdf)")
