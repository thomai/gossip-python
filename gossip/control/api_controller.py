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
from gossip.util.message_code import MESSAGE_CODE_ANNOUNCE, MESSAGE_CODE_NOTIFY, MESSAGE_CODE_VALIDATION
from gossip.util.queue_item_types import QUEUE_ITEM_TYPE_SEND_MESSAGE, QUEUE_ITEM_TYPE_CONNECTION_LOST, \
    QUEUE_ITEM_TYPE_RECEIVED_MESSAGE

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class APIController(multiprocessing.Process):
    def __init__(self, from_api_queue, to_api_queue, to_p2p_queue, api_connection_pool, p2p_connection_pool,
                 announce_message_cache, api_registration_handler):
        """ This controller is responsible for all incoming messages from the API layer. If an API client sends any
        message, this controller handles it in various ways.

        :param from_api_queue: Used by the API layer for incoming messages and commands
        :param to_api_queue: Messages and commands for the API layer are sent through this queue
        :param to_p2p_queue: Messages and commands for the P2P layer are sent through this queue
        :param api_connection_pool: Pool which contains all API connections/clients/sockets
        :param p2p_connection_pool: Pool which contains all P2P connections/clients/sockets
        :param announce_message_cache: Message cache which contains announce messages.
        :param api_registration_handler: Used for registrations (via NOTIFY message) from API clients
        """
        multiprocessing.Process.__init__(self)
        self.from_api_queue = from_api_queue
        self.to_api_queue = to_api_queue
        self.to_p2p_queue = to_p2p_queue
        self.api_connection_pool = api_connection_pool
        self.p2p_connection_pool = p2p_connection_pool
        self.announce_message_cache = announce_message_cache
        self.api_registration_handler = api_registration_handler

    def run(self):
        """ Typical run method which is used to handle API messages and commands. It reacts on incoming messages with
        changing the state of Gossip internally or by sending new messages resp. establishing new connections. """
        logging.info('%s started - PID: %s' % (type(self).__name__, self.pid))
        while True:
            queue_item = self.from_api_queue.get()
            queue_item_type = queue_item['type']
            message = queue_item['message']
            senders_identifier = queue_item['identifier']

            if queue_item_type == QUEUE_ITEM_TYPE_RECEIVED_MESSAGE:
                msg_code = message.get_values()['code']

                if msg_code == MESSAGE_CODE_ANNOUNCE:
                    logging.debug('APIController | Handle received announce (%d): %s' % (MESSAGE_CODE_ANNOUNCE,
                                                                                         message))

                    # Spread message via API layer (only registered clients) if it's unknown until now
                    msg_id = self.announce_message_cache.add_message(message, valid=True)

                    if msg_id:
                        logging.info('APIController | Spread message (id: %d) through API layer' % msg_id)

                        # Communication with API clients works with notification messages only. Therefore we have to
                        # convert the announce message.
                        notification_msg = convert.from_announce_to_notification(msg_id, message)
                        for receiver in self.api_registration_handler.get_registrations(message.data_type):
                            if receiver != senders_identifier:
                                self.to_api_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE, 'identifier': receiver,
                                                       'message': notification_msg})

                        # Spread message via P2P layer (all peers!)
                        logging.info('APIController | Spread message (id: %d) through P2P layer' % msg_id)
                        for receiver in self.p2p_connection_pool.get_identifiers():
                            self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE, 'identifier': receiver,
                                                   'message': message})
                    else:
                        logging.info('APIController | Discard message (already known).')

                elif msg_code == MESSAGE_CODE_NOTIFY:
                    logging.debug('APIController | Handle received notify (%d): %s' % (MESSAGE_CODE_NOTIFY, message))
                    msg_type = message.data_type
                    self.api_registration_handler.register(msg_type, senders_identifier)
                    logging.debug('APIController | API client is registered for message code %d now' % msg_type)
                    # Api client has registered, send him all messages that are in cache currently
                    for known_message in self.announce_message_cache.iterator(exclude_id=False):
                        notification_msg = convert.from_announce_to_notification(known_message[0],
                                                                                 known_message[1]["message"])
                        self.spread_message_to_api(notification_msg, senders_identifier)
                    # TODO: Delete the registration again if the connection has been terminated!

                elif msg_code == MESSAGE_CODE_VALIDATION:
                    logging.debug('APIController | Handle received validation (%d): %s' % (MESSAGE_CODE_VALIDATION,
                                                                                           message))

                    msg_id = message.get_values()['id']
                    # React on validation only if we haven't done that already
                    if not self.announce_message_cache.is_valid(msg_id):
                        if message.get_values()['valid']:
                            # Mark message as valid
                            self.announce_message_cache.set_validity(msg_id, True)
                            logging.debug('APIController | Message is valid (id: %d)' % msg_id)

                            # Spread message if it's still present in the cache
                            message_to_spread = self.announce_message_cache.get_message(msg_id)
                            if message_to_spread:
                                # Spread message over P2P layer
                                logging.info('APIController | Spread message (id: %d) through P2P layer' % msg_id)
                                # TODO: Don't send the message to the original sender! Exclude his identifier!
                                for identifier in self.p2p_connection_pool.get_identifiers():
                                    self.to_p2p_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE,
                                                           'identifier': identifier, 'message': message_to_spread})
                            else:
                                logging.debug('APIController | Message (id: %d) not in cache anymore.'
                                              ' Spreading impossible' % msg_id)
                        else:
                            logging.debug('APIController | Message is invalid (id: %d)' % msg_id)
                            self.announce_message_cache.remove_message(msg_id)
                    else:
                        logging.debug('APIController | Already spreaded the message (id: %d)' % msg_id)

                else:
                    logging.debug('APIController | Discarding message: %s' % message)
            elif queue_item_type == QUEUE_ITEM_TYPE_CONNECTION_LOST:
                self.api_registration_handler.unregister(senders_identifier)
                logging.debug('APIController | Lost an API connection: %s' % senders_identifier)

    @staticmethod
    def fetch_identifiers(connection_pool, server_to_exclude):
        """ Collects server identifiers
        :param connection_pool: The connection pool to iterate through
        :param server_to_exclude: Server identifier to exclude
        """
        for identifier in connection_pool.get_identifiers():
            server_address = connection_pool.get_connection(identifier)['server_address']
            if server_address != server_to_exclude:
                yield server_address

    def spread_message_to_api(self, notification_msg, senders_identifier):
        """ Spreads a message to all API clients which are registered for the containing message type.

        :param notification_msg: This message will be spread through all desired API clients
        :param senders_identifier: This identifier will be excluded from the receivers list
        """
        logging.debug("APIControllor | Spreading known messages to api")
        for receiver in self.api_registration_handler.get_registrations(notification_msg.data_type):
            # Only send messages to newly registered api!
            if receiver == senders_identifier:
                self.to_api_queue.put({'type': QUEUE_ITEM_TYPE_SEND_MESSAGE, 'identifier': receiver,
                                       'message': notification_msg})
