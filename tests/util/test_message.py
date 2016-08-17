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

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class TestMessageGossipAnnounce(unittest.TestCase):
    """
    Test class for MessageGossipAnnounce class
    """

    def test_encode_and_decode_of_message(self):
        """
        Tests if a MessageGossipAnnounce can be encoded and properly decoded
        :return: None
        """
        # values = packing.pack_gossip_announce(0, 540, 'p2p is very cool!')
        # msg_500 = message.MessageGossipAnnounce(values['data'])
        # msg_500_enc = msg_500.encode()
        # msg_500_dec = message.MessageGossipAnnounce(data=msg_500_enc[4:])
        # assert msg_500_dec.code == msg_500.code, "expected %s but was %s" % (msg_500_dec.code, msg_500.code)
        # assert msg_500_dec.data == msg_500.data, "expected %s but was %s" % (msg_500_dec.data, msg_500.data)
        pass

class TestMessageGossipNotify(unittest.TestCase):
    """
    Test class for MessageGossipNotify class
    """

    def test_encode_and_decode_of_message(self):
        """
        Tests if a MessageGossipNotify can be encoded and properly decoded
        :return: None
        """
        # values = packing.pack_gossip_notify(540)
        # msg = message.MessageGossipNotify(values['data'])
        # msg_enc = msg.encode()
        # msg_501 = message.MessageGossipNotify(values['data'])
        # msg_501_enc = msg_501.encode()
        # msg_501_dec = message.MessageGossipNotify(data=msg_501_enc[4:])
        # assert msg_501_dec.code == msg_501.code, "expected %s but was %s" % (msg_501_dec.code, msg_501.code)
        # assert msg_501_dec.data == msg_501.data, "expected %s but was %s" % (msg_501_dec.data, msg_501.data)
        pass
