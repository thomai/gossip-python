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

import unittest

from gossip.control.message_cache import GossipMessageCache

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class TestMessageCache(unittest.TestCase):
    """
    Test class for GossipMessageCache class
    """

    def test_maintain_message_cache(self):
        """
            This test method adds up to four messages to a pool with a maximum size of 3
            It fails if after adding the fourth message, the message pool is larger than 3 and
            if any other message, instead of the first one that has been added, was removed
            :return: None
        """
        max_pool_size = 3
        message_cache = GossipMessageCache('TestCache1', max_pool_size)

        id1 = message_cache.add_message("Msg1")
        id2 = message_cache.add_message("Msg2")

        cache_size = len(message_cache._msg_cache)
        assert cache_size == 2, "expected cache_size to be %s but was %s" % (max_pool_size, cache_size)

        id3 = message_cache.add_message("Msg3")
        id4 = message_cache.add_message("Msg4")

        cache_size = len(message_cache._msg_cache)
        assert cache_size == max_pool_size, "expected pool size to be %s but was %s" % (max_pool_size, cache_size)

        assert not message_cache.get_message(id1), "Expected first message added to be deleted but wasn't"
        assert message_cache.get_message(id2), "Expected second message added to be deleted but wasn't"
        assert message_cache.get_message(id3), "Expected third message added to be deleted but wasn't"
        assert message_cache.get_message(id4), "Expected fourth message added to be deleted but wasn't"
