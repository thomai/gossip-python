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

import multiprocessing
import logging

from gossip.control import convert
from gossip.util.message import MessageGossipPeerResponse, MessageGossipPeerRequest, MessageGossipPeerInit, \
    MessageGossipPeerUpdate, MessageGossipAnnounce
from gossip.util.packing import pack_gossip_peer_response, pack_gossip_peer_request, pack_gossip_peer_init, \
    pack_gossip_peer_update, pack_gossip_announce, PEER_UPDATE_TYPE_PEER_LOST, PEER_UPDATE_TYPE_PEER_FOUND
from gossip.util.message_code import MESSAGE_CODE_ANNOUNCE, MESSAGE_CODE_PEER_REQUEST, MESSAGE_CODE_PEER_RESPONSE, \
    MESSAGE_CODE_PEER_UPDATE, MESSAGE_CODE_PEER_INIT
from gossip.util.queue_item_types import QUEUE_ITEM_TYPE_SEND_MESSAGE, QUEUE_ITEM_TYPE_CONNECTION_LOST, \
    QUEUE_ITEM_TYPE_RECEIVED_MESSAGE, QUEUE_ITEM_TYPE_ESTABLISH_CONNECTION, QUEUE_ITEM_TYPE_NEW_CONNECTION

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class P2PController(multiprocessing.Process):
    def __init__(self, from_p2p_queue, to_p2p_queue, to_api_queue, p2p_connection_pool, p2p_server_address,
                 announce_message_cache, update_message_cache, api_registration_handler, max_ttl,
                 bootstrapper_address=None):
        """ This controller is responsible for all incoming messages from the P2P layer. If a P2P client sends any
        message, this controller handles it in various ways.

        :param from_p2p_queue: Used by the P2P layer for incoming messages and commands
        :param to_p2p_queue: Messages and commands for the P2P layer are sent through this queue
        :param to_api_queue: Messages and commands for the API layer are sent through this queue
        :param p2p_connection_pool: Pool which contains all P2P connections/clients/sockets
        :param p2p_server_address: The P2P server address for this gossip instance
        :param announce_message_cache: Message cache which contains announce messages.
        :param update_message_cache: Message cache for peer update messages
        :param api_registration_handler: Used for registrations (via NOTIFY message) from API clients
        :param max_ttl: Max. amount of hops until messages will be dropped
        :param bootstrapper_address: (optional) dict to specify the bootstrapper {'host': <IPv4>: 'port': <int(port)>}
        """
        multiprocessing.Process.__init__(self)
        self.from_p2p_queue = from_p2p_queue
        self.to_p2p_queue = to_p2p_queue
        self.to_api_queue = to_api_queue
        self.p2p_connection_pool = p2p_connection_pool
        self.p2p_server_address = p2p_server_address
        self.announce_message_cache = announce_message_cache
        self.update_message_cache = update_message_cache
        self.api_registration_handler = api_registration_handler
        self.max_ttl = max_ttl
        self.bootstrapper_address = bootstrapper_address

    def run(self):
        """ Typical run method which is used to handle P2P messages and commands. It reacts on incoming messages with
        changing the state of Gossip internally or by sending new messages resp. establishing new connections. """
        logging.info('%s started - PID: %s' % (type(self).__name__, self.pid))

        # Bootstrapping part
        if self.bootstrapper_address:
            bootstrapper_identifier = '%s:%d' % (self.bootstrapper_address['host'], self.bootstrapper_address['port'])
            self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_ESTABLISH_CONNECTION, 'identifier': bootstrapper_identifier})
            self.send_peer_request(bootstrapper_identifier)

        # Usual controller part
        while True:
            queue_item = self.from_p2p_queue.get()
            queue_item_type = queue_item['type']
            message = queue_item['message']
            senders_identifier = queue_item['identifier']

            if queue_item_type == QUEUE_ITEM_TYPE_RECEIVED_MESSAGE:
                msg_code = message.get_values()['code']

                if msg_code == MESSAGE_CODE_ANNOUNCE:
                    logging.debug('P2PController | Handle received announce (%d): %s' % (MESSAGE_CODE_ANNOUNCE,
                                                                                         message))

                    # Spread message via API layer (only registered clients) if it's unknown until now
                    msg_id = self.announce_message_cache.add_message(message)

                    if msg_id:
                        logging.info('P2PController | Spread message (id: %d) through API layer' % msg_id)

                        # Change ttl and create new announce message
                        ttl = message.get_values()['TTL']
                        if ttl > 1 or ttl == 0:
                            ttl = ttl-1 if ttl > 1 else 0
                            packed_announce_msg = pack_gossip_announce(ttl, message.get_values()['type'],
                                                                       message.get_values()['message'])['data']
                            announce_msg = MessageGossipAnnounce(packed_announce_msg)

                            # Communication with API clients works with notification messages only. Therefore we have to
                            # convert the announce message.
                            notification_msg = convert.from_announce_to_notification(msg_id, announce_msg)
                            for receiver in self.api_registration_handler.get_registrations(message.data_type):
                                if receiver != senders_identifier:
                                    self.to_api_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE, 'identifier': receiver,
                                                           'message': notification_msg})
                    else:
                        logging.info('P2PController | Discard message (already known).')

                elif msg_code == MESSAGE_CODE_PEER_REQUEST:
                    # Someone wants to know our known identifiers
                    logging.debug('P2PController | Handle received peer request (%d): %s' % (MESSAGE_CODE_PEER_REQUEST,
                                                                                             message))

                    # The peer request message contains the server address of the other peer
                    peer_server_identifier = message.get_values()['p2p_server_address']
                    self.p2p_connection_pool.update_connection(senders_identifier, peer_server_identifier)

                    # Build identifier list BUT exclude the identifier of the requesting peer!
                    own_p2p_server_identifier = '%s:%d' % (self.p2p_server_address['host'],
                                                           self.p2p_server_address['port'])
                    known_server_identifiers = self.p2p_connection_pool.get_server_identifiers(
                        identifier_to_exclude=[peer_server_identifier, own_p2p_server_identifier])

                    # Send the assembled identifier list
                    packed_data = pack_gossip_peer_response(known_server_identifiers)['data']
                    peer_response_msg = MessageGossipPeerResponse(packed_data)
                    self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE, 'identifier': senders_identifier,
                                           'message': peer_response_msg})
                    logging.debug('P2PController | Answering with peer response (%d): %s' % (MESSAGE_CODE_PEER_RESPONSE,
                                                                                             peer_response_msg))

                    # We've got the server identifier with the peer request, so spread it to anyone we know
                    senders_server_identifier = self.p2p_connection_pool.get_server_identifier(senders_identifier)
                    self.send_peer_update(senders_identifier, senders_server_identifier, self.max_ttl)

                elif msg_code == MESSAGE_CODE_PEER_INIT:
                    # Someone wants to inform us about his server identifier
                    logging.debug('P2PController | Handle received peer init (%d): %s' % (MESSAGE_CODE_PEER_INIT,
                                                                                          message))

                    # The peer request message contains the server address of the other peer
                    peer_server_identifier = message.get_values()['p2p_server_address']
                    self.p2p_connection_pool.update_connection(senders_identifier, peer_server_identifier)

                    # We've got the server identifier with the peer init, so spread it to anyone we know
                    senders_server_identifier = self.p2p_connection_pool.get_server_identifier(senders_identifier)
                    self.send_peer_update(senders_identifier, senders_server_identifier, self.max_ttl)

                elif msg_code == MESSAGE_CODE_PEER_RESPONSE:
                    # We received the known identifiers of someone
                    logging.debug('P2PController | Handle received peer response (%d): %s'
                                  % (MESSAGE_CODE_PEER_RESPONSE, message))

                    # Use the peer response only if there is space for new connections in the pool
                    if self.p2p_connection_pool.get_capacity() > 0:
                        received_server_identifiers = message.get_values()['data']
                        new_identifiers = self.p2p_connection_pool.filter_new_server_identifiers(
                            received_server_identifiers)

                        # If the peer response provides new identifiers, we establish a new connection with them
                        if len(new_identifiers) > 0:
                            for new_identifier in new_identifiers:
                                self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_ESTABLISH_CONNECTION,
                                                       'identifier': new_identifier})

                                # Send initial message
                                logging.debug('P2PController | Sending peer init (%d): %s' % (MESSAGE_CODE_PEER_INIT,
                                                                                              message))
                                own_p2p_server_identifier = '%s:%d' % (self.p2p_server_address['host'],
                                                                       self.p2p_server_address['port'])
                                packed_data = pack_gossip_peer_init(own_p2p_server_identifier)['data']
                                self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE,
                                                       'identifier': new_identifier,
                                                       'message': MessageGossipPeerInit(packed_data)})

                                # Stop if the pool is full
                                if self.p2p_connection_pool.get_capacity() <= 0:
                                    break
                    else:
                        logging.debug('P2PController | Discarding message (%d) because pool is full!' % msg_code)

                elif msg_code == MESSAGE_CODE_PEER_UPDATE:
                    # We received a peer update of someone
                    logging.debug('P2PController | Handle received peer update (%d): %s' % (MESSAGE_CODE_PEER_UPDATE,
                                                                                            message))

                    new_server_identifier = message.get_values()['address']
                    update_type = message.get_values()['update_type']
                    ttl = message.get_values()['ttl']

                    if ttl < int(self.max_ttl/2):
                        if update_type == PEER_UPDATE_TYPE_PEER_FOUND:
                            # Use the peer update only if there is space for a new connection in the pool
                            if self.p2p_connection_pool.get_capacity() > 0:
                                new_identifiers = self.p2p_connection_pool.filter_new_server_identifiers(
                                    [new_server_identifier])

                                # If the peer update provides a new identifier, we establish a new connection with it
                                for new_identifier in new_identifiers:
                                    self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_ESTABLISH_CONNECTION,
                                                           'identifier': new_identifier})

                                    # Send initial message
                                    logging.debug('P2PController | Sending peer init (%d): %s' % (MESSAGE_CODE_PEER_INIT,
                                                                                                  message))
                                    own_p2p_server_identifier = '%s:%d' % (self.p2p_server_address['host'],
                                                                           self.p2p_server_address['port'])
                                    packed_data = pack_gossip_peer_init(own_p2p_server_identifier)['data']
                                    self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE,
                                                           'identifier': new_identifier,
                                                           'message': MessageGossipPeerInit(packed_data)})
                            else:
                                logging.debug('P2PController | Discarding message (%d) because pool is full' % msg_code)
                        elif update_type == PEER_UPDATE_TYPE_PEER_LOST:
                            # Currently a peer update of type PEER_UPDATE_TYPE_PEER_LOST does not need to be handled
                            pass

                    # If we don't know the peer update already, spread it
                    if ttl > 1:
                        ttl -= 1
                        self.send_peer_update(senders_identifier, new_server_identifier, ttl)
                    elif ttl == 0:  # A ttl of 0 means that the message is unstoppable!
                        self.send_peer_update(senders_identifier, new_server_identifier, ttl)

                else:
                    logging.debug('P2PController | Discarding message (%d)' % msg_code)

            elif queue_item_type == QUEUE_ITEM_TYPE_CONNECTION_LOST:
                # A connection has been disconnected from this instance
                logging.debug('P2PController | One connection lost, try to get a new one %s' % senders_identifier)

                random_identifier = self.p2p_connection_pool.get_random_identifier(senders_identifier)
                if random_identifier:
                    self.send_peer_request(random_identifier)

            elif queue_item_type == QUEUE_ITEM_TYPE_NEW_CONNECTION:
                # Our instance know a new connection
                senders_server_identifier = self.p2p_connection_pool.get_server_identifier(senders_identifier)
                # We can inform everyone only if we know the server identifier of the sender
                if senders_server_identifier:
                    self.send_peer_update(senders_identifier, senders_server_identifier, self.max_ttl)
                else:
                    logging.debug('P2PController | Don\'t know the server identifier of the new connection, wait for'
                                  ' peer server address of %s' % senders_identifier)

                self.exchange_messages(senders_identifier)

    def send_peer_update(self, senders_identifier, senders_server_identifier, ttl):
        """ Sends peer updates to several peers.

        :param senders_identifier: Identifier of the sender we received this update from
        :param senders_server_identifier: Server identifier of the changed peer
        :param ttl: ttl to set in the new update messages
        """
        packed_data = pack_gossip_peer_update(senders_server_identifier, ttl, PEER_UPDATE_TYPE_PEER_FOUND)['data']
        peer_update_msg = MessageGossipPeerUpdate(packed_data)
        msg_id = self.update_message_cache.add_message(peer_update_msg, valid=True)

        if msg_id and senders_server_identifier != '%s:%d' % (self.p2p_server_address['host'],
                                                              self.p2p_server_address['port']):
            logging.debug('P2PController | Spread information about new connection %s' % senders_identifier)
            identifiers = self.p2p_connection_pool.get_identifiers()
            for identifier in identifiers:
                if identifier not in [senders_identifier, senders_server_identifier]:
                    self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE, 'identifier': identifier,
                                           'message': peer_update_msg})

    def send_peer_request(self, peer_request_identifier):
        """ Sends a peer request

        :param peer_request_identifier: The identifier dict of the receiving peer
        """
        own_p2p_server_identifier = '%s:%d' % (self.p2p_server_address['host'], self.p2p_server_address['port'])
        packed_msg = pack_gossip_peer_request(own_p2p_server_identifier)
        peer_request_msg = MessageGossipPeerRequest(packed_msg['data'])
        self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE, 'identifier': peer_request_identifier,
                               'message': peer_request_msg})

    def exchange_messages(self, peer_identifier):
        """ Send messages to new connected peer.

        :param peer_identifier: Receiving peer
        """
        logging.debug('P2PController | Exchanging messages with (%s)' % peer_identifier)
        for message in self.announce_message_cache.iterator():
            self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE, 'identifier': peer_identifier,
                                   'message': message["message"]})
