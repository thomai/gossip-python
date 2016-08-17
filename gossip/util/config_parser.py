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

from configparser import RawConfigParser
import logging

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


def split_host_address(host_address):
    """ Splits a host address into the host and the corresponding port (as int) in the form of a dictionary

    :returns: A dict in the form {'host': <IP OR HOSTNAME> 'port': <PORT as int>}
    """
    if ':' not in host_address:
        return None
    host, port = host_address.split(':')
    return {'host': host, 'port': int(port)}


def read_config(config_path):
    """ Reads the INI configuration file and returns all settings as a dict

    :param config_path: File path of the INI file.
    :returns: A dict in the form {<CONFIG SETTING>: <VALUE>, ...}
    """
    logging.debug('Parsing gossip configuration file.')
    config_parser = RawConfigParser()
    config_parser.read(config_path)

    # Parse INI file
    hostkey = config_parser.get('GLOBAL', 'HOSTKEY')
    cache_size = config_parser.getint('GOSSIP', 'cache_size')
    max_connections = config_parser.getint('GOSSIP', 'max_connections')
    bootstrapper = split_host_address(config_parser.get('GOSSIP', 'bootstrapper'))
    listen_address = split_host_address(config_parser.get('GOSSIP', 'listen_address'))
    api_address = split_host_address(config_parser.get('GOSSIP', 'api_address'))
    max_ttl = int(config_parser.get('GOSSIP', 'max_ttl'))

    # Build dictionary
    config = {'hostkey': hostkey, 'cache_size': cache_size, 'max_connections': max_connections,
              'bootstrapper': bootstrapper, 'listen_address': listen_address, 'api_address': api_address,
              'max_ttl': max_ttl}

    return config
