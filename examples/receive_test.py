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
from gossip.util import packing, message

__author__ = 'Anselm Binninger, Ralph Schaumann, Thomas Maier'

try:
    while True:
        sock = socket.socket()
        sock.connect(('localhost', 6001))
        values = packing.receive_msg(sock)
        message_object = message.GOSSIP_MESSAGE_TYPES.get(values['code'], message.MessageOther)
        if 500 <= values['code'] < 520:
            print(message_object(values['message']))
        else:
            print(values)
        sock.close()
except Exception as e:
    print('%s' % e)
