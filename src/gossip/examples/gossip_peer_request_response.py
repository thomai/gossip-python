#!/usr/bin/env python3
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

import socket

from gossip.util import packing
from gossip.util import message

__author__ = 'Anselm Binninger, Ralph Schaumann, Thomas Maier'

sock1 = socket.socket()
sock2 = socket.socket()
sock1.connect(('127.0.0.1', 6001))
sock2.connect(('127.0.0.1', 6001))
values = packing.pack_gossip_peer_request()
packing.send_msg(sock1, values['code'], values['data'])
values = packing.receive_msg(sock1)
print(values)
message_object = message.MessageGossipPeerResponse(values['message'])
value = message_object.get_values()
print(message_object.connections)
sock1.close()
sock2.close()
