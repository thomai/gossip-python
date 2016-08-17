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
import logging.config
import os
import signal
import sys
from argparse import ArgumentParser
from multiprocessing import Queue

from gossip.communication.server import GossipServer
from gossip.communication.client_sender import GossipSender
from gossip.communication.connection import GossipConnectionPool
from gossip.control.api_controller import APIController
from gossip.control.p2p_controller import P2PController
from gossip.control.message_cache import GossipMessageCache
from gossip.control.api_registrations import APIRegistrationHandler
from gossip.util import config_parser

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'

DEFAULT_CONFIG_PATH = 'config/config.ini'

logging.config.fileConfig('config/logging_config.ini')


def signal_handler(signal, frame):
    logging.error('Stopping gossip process - PID: %s', (os.getpid()))
    sys.exit(0)


def main():
    cli_parser = ArgumentParser()
    cli_parser.add_argument('-c', '--config', help='Configuration file path', default=DEFAULT_CONFIG_PATH)
    cli_args = cli_parser.parse_args()
    config_file_path = cli_args.config

    # Check cli arguments
    if not os.path.isfile(config_file_path):
        logging.error('The given config file does not exist: %s', config_file_path)
        sys.exit(1)

    """ Runs the gossip module. """
    logging.info('Starting gossip main process - PID: %s', (os.getpid()))

    # Register SIGINT signal
    signal.signal(signal.SIGINT, signal_handler)

    # Read
    gossip_config = config_parser.read_config(config_file_path)

    # Gossip layers with queues between them:
    #
    #          <---- API connections <----
    #         v                           ^
    #     APIServer                   APISender
    #         v                           ^
    #  ----------------            ----------------
    # | API2Controller |          | Controller2API |
    #  ----------------            ----------------
    #         v                           ^
    #    APIController               P2PController
    #         v                           ^
    #  ----------------            ----------------
    # | Controller2P2P |          | P2P2Controller |
    #  ----------------            ----------------
    #         v                           ^
    #     P2PSender                   P2PServer
    #         v                           ^
    #          ----> P2P connections ---->

    api_server_address = gossip_config['api_address']
    p2p_server_address = gossip_config['listen_address']
    bootstrapper_address = gossip_config['bootstrapper']
    max_connections = gossip_config['max_connections']
    cache_size = gossip_config['cache_size']
    max_ttl = gossip_config['max_ttl']

    api_connection_pool = GossipConnectionPool('APIConnectionPool', cache_size=max_connections)
    p2p_connection_pool = GossipConnectionPool('P2PConnectionPool', cache_size=max_connections)
    announce_message_cache = GossipMessageCache('AnnounceMessageCache', cache_size=cache_size)
    update_message_cache = GossipMessageCache('UpdateMessageCache', cache_size=cache_size)

    api_registration_handler = APIRegistrationHandler()

    # Layers for incoming API connections/messages
    api_to_controller = Queue()
    api_server = GossipServer('APIServer', 'APIClientReceiver', api_server_address['host'], api_server_address['port'],
                              api_to_controller, api_connection_pool)
    controller_to_p2p = Queue()
    controller_to_api = Queue()
    api_controller = APIController(api_to_controller, controller_to_api, controller_to_p2p, api_connection_pool,
                                   p2p_connection_pool, announce_message_cache, api_registration_handler)
    p2p_to_controller = Queue()
    p2p_sender = GossipSender('P2PSender', controller_to_p2p, p2p_to_controller, p2p_connection_pool)

    # Layers for incoming P2P connections/messages
    p2p_server = GossipServer('P2PServer', 'P2PClientReceiver', p2p_server_address['host'], p2p_server_address['port'],
                              p2p_to_controller, p2p_connection_pool)
    p2p_controller = P2PController(p2p_to_controller, controller_to_p2p, controller_to_api, p2p_connection_pool,
                                   p2p_server_address, announce_message_cache, update_message_cache,
                                   api_registration_handler, max_ttl, bootstrapper_address=bootstrapper_address)
    api_sender = GossipSender('APISender', controller_to_api, api_to_controller, api_connection_pool)

    api_server.start()
    api_controller.start()
    p2p_sender.start()
    p2p_server.start()
    p2p_controller.start()
    api_sender.start()

    api_server.join()
    api_controller.join()
    p2p_sender.join()
    p2p_server.join()
    p2p_controller.join()
    api_sender.join()

    # Handle exit codes
    exit_codes = api_server.exitcode | api_controller.exitcode | p2p_sender.exitcode
    exit_codes = exit_codes | p2p_server.exitcode | p2p_controller.exitcode | api_sender.exitcode

    if exit_codes > 0:
        logging.error('Gossip subprocess exited with return code %d', exit_codes)
    else:
        logging.info('Gossip exited with return code %d', exit_codes)

    sys.exit(exit_codes)
