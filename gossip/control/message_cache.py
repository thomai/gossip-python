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
from multiprocessing import Manager
from random import randrange

from datetime import datetime

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class GossipMessageCache:
    """Thread-safe implementation of a message cache which maintains all currently known messages."""

    DATE_ADDED = 'DateAdded'
    MAX_MSG_ID = 65535

    def __init__(self, message_cache_label, cache_size=30):
        """Contructor.

        :param cache_size: The maximum numbers of messages that can be hold by this cache: Default 30
        """
        self._msg_cache = Manager().dict()
        self._message_cache_label = message_cache_label
        self._cache_size = cache_size

    def add_message(self, message, valid=False):
        """ Adds new message to the cache.

        :param message: The new message to cache
        :param valid: (optional) Flag which states whether this message is valid or not
        :returns: The generated random message identifier for the cached message (None if message is already in cache)
        """
        # If the message exists already in the cache, return None
        for msg_id in self._msg_cache.keys():
            if message == self._msg_cache[msg_id]['message']:
                return None

        # Generate a message id which isn't in the cache already
        msg_id = randrange(0, self.MAX_MSG_ID)
        while msg_id in self._msg_cache.keys():
            msg_id = randrange(0, self.MAX_MSG_ID)
        self._msg_cache[msg_id] = {'message': message, 'valid': valid,
                                   GossipMessageCache.DATE_ADDED: datetime.now()}

        self.__maintain_cache()
        logging.debug('%s | Added new message, current message cache: %s' % (self._message_cache_label,
                                                                             self._msg_cache.keys()))
        return msg_id

    def get_message(self, msg_id):
        """ Provides a cached message.

        :param msg_id: Identifier of the desired message
        :returns: The desired message (None if it does not exist)
        """
        logging.debug('%s | Current message cache: %s' % (self._message_cache_label, self._msg_cache.keys()))
        if msg_id in self._msg_cache:
            return self._msg_cache[msg_id]['message']
        else:
            return None

    def is_valid(self, msg_id):
        """ Returns True if the specified message is marked as valid

        :param msg_id: Message id
        :returns: True if the message is marked as valid, False if it is invalid or if it doesn't exist in the cache
        """
        if msg_id in self._msg_cache:
            return self._msg_cache[msg_id]['valid']
        else:
            return False

    def set_validity(self, msg_id, valid):
        """ Sets validity for a specific message.

        :param msg_id: Identifier of the message
        :param valid: Flag which states whether the specified message is valid or not
        """
        if msg_id in self._msg_cache:
            old_cache_item = self._msg_cache[msg_id]
            old_cache_item['valid'] = valid
            self._msg_cache[msg_id] = old_cache_item

    def remove_message(self, msg_id):
        """ Removes a message from the cache.

        :param msg_id: Identifier of the message
        :returns: Removed message (None if it does not exist)
        """
        return self._msg_cache.pop(msg_id, None)

    def __maintain_cache(self):
        """ Maintains the message cache. If the cache exceeds the defined maximum the oldest message is removed from the
        cache """
        if len(self._msg_cache) > self._cache_size:
            sorted_messages = sorted(self._msg_cache.items(),
                                     key=lambda x: self._msg_cache[x[0]][GossipMessageCache.DATE_ADDED])
            message_to_remove = sorted_messages[0][0]
            self.remove_message(message_to_remove)

    def iterator(self, exclude_id=True):
        """ Creates a generator for the message cache. Removes the outer dict with id and only returns message ordered
        by date (from oldest to newest)

        :return: An iterator over the ordered list of messages
        """
        sorted_messages = sorted(self._msg_cache.items(),
                                 key=lambda x: self._msg_cache[x[0]][GossipMessageCache.DATE_ADDED])
        return (message[1] if exclude_id else message for message in sorted_messages)
