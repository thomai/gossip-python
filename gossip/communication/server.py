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
import multiprocessing
import socket

from gossip.communication.client_receiver import GossipClientReceiver

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class GossipServer(multiprocessing.Process):
    def __init__(self, server_label, client_receiver_label, bind_address, tcp_port, to_controller_queue,
                 connection_pool):
        """ The Gossip server waits for new connections established by other clients. It also instantiates new receivers
        for incoming connections.

        :param server_label: A label to derive the concrete functionality of this gossip server
        :param client_receiver_label: This label is used for newly instantiated receivers
        :param bind_address: IPv4 address which is used to listen for new connections
        :param tcp_port: TCP port which is used to listen for new connections
        :param to_controller_queue: Newly instantiated receivers need to know a queue to communicate with the controller
        :param connection_pool: New connections will be added to the appropriate connection pool
        """
        multiprocessing.Process.__init__(self)
        self.server_label = server_label
        self.client_receiver_label = client_receiver_label
        self.bind_address = bind_address
        self.tcp_port = tcp_port
        self.to_controller_queue = to_controller_queue
        self.connection_pool = connection_pool

    def run(self):
        """ Typical run method for the sender process. It waits for new connections, refers to newly instantiated
        receiver instances, and finally starts the new receivers. """
        try:
            logging.info('%s started (%s:%d) - PID: %s' % (self.server_label, self.bind_address, self.tcp_port,
                                                           self.pid))
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.bind_address, self.tcp_port))
            server_socket.listen(5)
            while True:
                client_socket, address = server_socket.accept()
                tcp_address, tcp_port = address
                connection_identifier = '%s:%d' % (tcp_address, tcp_port)
                self.connection_pool.add_connection(connection_identifier, client_socket)
                logging.info("%s | Added new connection to connection pool" % self.server_label)
                client_receiver = GossipClientReceiver(self.client_receiver_label, client_socket, tcp_address, tcp_port,
                                                       self.to_controller_queue, self.connection_pool)
                client_receiver.start()
            server_socket.close()
        except OSError as os_error:
            logging.error('%s crashed (%s:%d) - PID: %s - %s' % (self.server_label, self.bind_address, self.tcp_port,
                                                                 self.pid, os_error))
