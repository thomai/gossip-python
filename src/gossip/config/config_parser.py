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

import os
import logging
import pathlib
from configparser import RawConfigParser

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


CONFIG_PATH_ENV_VARIABLE = "GOSSIP_CONFIG_PATH"
PREFERED_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.gossip' )
DEFAULT_CONFIG_SEARCH_PATH = [
    'config/config.ini', # Maintained for backwards compatibility
    os.path.join(os.path.expanduser('~'), '.gossip' ),
    os.path.join(os.path.expanduser('~'), '.config/gossip' )
]
DEFAULT_CONFIG_FILE_NAME = 'config.ini'
DEFAULT_LOGGING_CONFIG_FILE_NAME = 'logging_config.ini'

def get_config_path(config_file_name, search_path=DEFAULT_CONFIG_SEARCH_PATH):
    """
    Determines the file path based on the environment variables specified by
    gossip_main.CONFIG_PATH_ENV_VARIABLE and a default search path.

    :param config_file_name: _description_
    :type config_file_name: _type_
    :param search_path: _description_, defaults to DEFAULT_CONFIG_SEARCH_PATH
    :type search_path: _type_, optional
    :return: The config file path or None.
    :rtype: str or None
    """
    config_path = None

    # Check to see if an environment variable has explicitly specified a path
    config_path = os.environ.get(os.path.join(CONFIG_PATH_ENV_VARIABLE, config_file_name), None)

    # If the config path has not been specified, check the search path for
    # for config.ini files.
    if not config_path:
        for path in search_path:
            file_path = os.path.join(path, config_file_name)
            if os.path.isfile(file_path):
                config_path = file_path
                break
    
    # If the config doesn't exist, 
    if not config_path:
        config_path = os.path.join(PREFERED_CONFIG_PATH, config_file_name)
        template_config = os.path.join(os.path.dirname(__file__), config_file_name)
        logging.warning("Config file %s not found in any search path. Copying template configuration from %s to %s.",
                        config_path, template_config, config_path)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w+', encoding='utf8') as new_config:
            with open(template_config, 'r', encoding='utf8') as template:
                new_config.write(template.read())

    # Return the path or None if no config file was found
    return config_path


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
