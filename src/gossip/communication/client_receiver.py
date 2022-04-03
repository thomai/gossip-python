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
from multiprocessing import Process

from gossip.util import packing
from gossip.util.exceptions import GossipMessageException, GossipClientDisconnectedException, \
    GossipMessageFormatException
from gossip.util.message import MessageOther
from gossip.util.message import GOSSIP_MESSAGE_TYPES
from gossip.util.queue_item_types import QUEUE_ITEM_TYPE_RECEIVED_MESSAGE, QUEUE_ITEM_TYPE_CONNECTION_LOST, \
    QUEUE_ITEM_TYPE_NEW_CONNECTION

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class GossipClientReceiver(Process):
    """ A client receiver is a process which receives data from a specified socket. """
    def __init__(self, client_receiver_label, client_socket, ipv4_address, tcp_port, to_controller_queue,
                 connection_pool):
        """ Constructor.

        :param client_receiver_label: A label to derive the concrete functionality of this client receiver
        :param client_socket: The socket from/to the affected the affected client
        :param ipv4_address: The IPv4 address of the client
        :param tcp_port: The TCP port of the client
        :param to_controller_queue: The queue which connects this client receiver with the responsible controller
        :param connection_pool: If the socket crashes, the connection will be removed in this connection pool
        """
        Process.__init__(self)
        self.client_receiver_label = client_receiver_label
        self.client_socket = client_socket
        self.identifier = '%s:%d' % (ipv4_address, tcp_port)
        self.to_controller_queue = to_controller_queue
        self.connection_pool = connection_pool

    def run(self):
        """ This typical run method of the client receiver process is responsible for handling a connection for
        the Gossip instance. It handles incoming messages and forwards them to the controller. If a connection crashes,
        this method pushes a specified command to the responsible controller. """
        logging.info('%s (%s) started' % (self.client_receiver_label, self.identifier))
        try:
            self.handle_client()
        except GossipClientDisconnectedException:
            logging.info('%s (%s) Removing connection from connection pool' % (self.client_receiver_label,
                                                                               self.identifier))
            self.connection_pool.remove_connection(self.identifier)
            self.to_controller_queue.put({'type': QUEUE_ITEM_TYPE_CONNECTION_LOST,
                                          'identifier': self.identifier,
                                          'message': None})

    def handle_client(self):
        """ Receives new messages until the client dies. It also kills connections to clients which send malformed
        messages. Therefor it informs the responsible controller as well. """
        self.to_controller_queue.put({'type': QUEUE_ITEM_TYPE_NEW_CONNECTION,
                                      'identifier': self.identifier,
                                      'message': None})
        try:
            while True:
                message = self.__receive()
                logging.debug('%s (%s) | Received message %s' % (self.client_receiver_label, self.identifier, message))
        except (GossipMessageException, GossipMessageFormatException) as e:
            logging.debug('%s (%s) | Received undecodable or invalid message: %s' % (self.client_receiver_label,
                                                                                     self.identifier, e))
            raise GossipClientDisconnectedException('Lost %s (%s)' % (self.client_receiver_label, self.identifier))
        except (ConnectionResetError, ConnectionAbortedError, GossipClientDisconnectedException):
            logging.debug('%s (%s) | Client disconnected' % (self.client_receiver_label, self.identifier))
            raise GossipClientDisconnectedException('Lost %s (%s)' % (self.client_receiver_label, self.identifier))

        self.client_socket.close()

    def __receive(self):
        """
        Receives a new message, unpacks it and forwards it to the assigned controller.

        :returns: The received message object
        """
        msg = packing.receive_msg(self.client_socket)
        if msg['code'] in GOSSIP_MESSAGE_TYPES.keys():
            try:
                message_object = GOSSIP_MESSAGE_TYPES[msg['code']](msg['message'])
            except Exception as e:
                # TODO Don't catch Exception, catch specific decoding exception
                raise GossipMessageFormatException('%s' % e)
        else:
            message_object = MessageOther(msg['code'], msg['message'])

        self.to_controller_queue.put({'type': QUEUE_ITEM_TYPE_RECEIVED_MESSAGE,
                                      'identifier': self.identifier,
                                      'message': message_object})
        return message_object
