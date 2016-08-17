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

from gossip.util.exceptions import GossipQueueException, GossipIdentifierNotFound
from gossip.util.queue_item_types import QUEUE_ITEM_TYPE_SEND_MESSAGE, QUEUE_ITEM_TYPE_ESTABLISH_CONNECTION
from gossip.communication.client_receiver import GossipClientReceiver

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class GossipSender(multiprocessing.Process):
    """ The Gossip sender receives new commands from the responsible controller. The sender is responsible for sending
    new messages to specified receivers. It is able to establish new connections as well if the controller sends the
    appropriate command to do so. """

    def __init__(self, sender_label, from_controller_queue, to_controller_queue, connection_pool):
        """ Constructor.

        :param sender_label: A label to derive the concrete functionality of this client sender
        :param from_controller_queue: The client sender gets new commands via this queue from the responsible controller
        :param to_controller_queue: This instance forwards the controller queue to new receiver instances
        :param connection_pool: The connection pool which contains all connections/sockets
        """
        multiprocessing.Process.__init__(self)
        self.sender_label = sender_label
        self.from_controller_queue = from_controller_queue
        self.to_controller_queue = to_controller_queue
        self.connection_pool = connection_pool

    def run(self):
        """ This is a typical run method for the sender process. It waits for commands from the controller to establish
        new connections or to send messages to established connections. The sender gets the appropriate
        connection/socket from the connection pool. """
        logging.info('%s started - PID: %s' % (self.sender_label, self.pid))

        while True:
            queue_item = self.from_controller_queue.get()
            queue_item_type = queue_item['type']
            identifier = queue_item['identifier']

            # Fetch the right connection
            if queue_item_type == QUEUE_ITEM_TYPE_SEND_MESSAGE:
                message = queue_item['message']

                # Fetch connection from connection pool
                logging.info("%s | Redirecting message (code %d) to corresponding client"
                             % (self.sender_label, message.get_values()['code']))
                try:
                    connection = self.connection_pool.get_connection(identifier)
                except GossipIdentifierNotFound:
                    connection = None

                # Send message
                if connection:
                    if message:
                        encoded = message.encode()
                        try:
                            connection.send(encoded)
                            logging.debug('%s | Sent message (%s) to client %s | Sent message: %s'
                                          % (self.sender_label, message.get_values()['code'], identifier,
                                             message.get_values()))
                        except (ConnectionResetError, ConnectionAbortedError):
                            self.connection_pool.remove_connection(identifier)
                            logging.error('%s | During sending a message peer disconnected' % self.sender_label)
                else:
                    logging.error('%s | No connection found in connection pool, giving up' % self.sender_label)

            elif queue_item_type == QUEUE_ITEM_TYPE_ESTABLISH_CONNECTION:
                # Establish new connection
                logging.info("%s Establishing new connection to %s" % (self.sender_label, identifier))
                connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_host, server_port = identifier.split(':')
                server_port = int(server_port)
                try:
                    connection.connect((server_host, server_port))
                    self.connection_pool.add_connection(identifier, connection, server_identifier=identifier)
                except ConnectionRefusedError:
                    logging.error('%s | Cannot establish connection to %s' % (self.sender_label, identifier))
                    continue

                logging.info("%s | Added new connection to connection pool" % self.sender_label)

                # Create client receiver for new connection
                # TODO Client receiver label should not be hardcoded here!
                client_receiver = GossipClientReceiver('P2PClientReceiver', connection, server_host, server_port,
                                                       self.to_controller_queue, self.connection_pool)

                client_receiver.start()

            else:
                # If this happens, someone did a horrible mistake in the code: The queue item type is not supported!
                raise GossipQueueException('%s: Queue item cannot be identified! This should never happen!'
                                           % self.sender_label)
