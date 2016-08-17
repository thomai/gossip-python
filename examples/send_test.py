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

import time

__author__ = 'Anselm Binninger, Ralph Schaumann, Thomas Maier'

try:
    
    port = 6001
    ip_address = 'localhost'

    print('sending garbage')
    sock = socket.socket()
    sock.connect((ip_address, port))
    sock.send(bytes('s', 'ascii'))
    sock.close()
    print('garbage sent')
    time.sleep(2)

    print('Sending 404')
    sock = socket.socket()
    sock.connect((ip_address, port))
    values = packing.pack_message_other(404, 'message not found')
    packing.send_msg(sock, values['code'], values['data'])
    sock.close()
    print('404 sent')
    time.sleep(2)

    print('Sending 500')
    sock = socket.socket()
    sock.connect((ip_address, port))
    values = packing.pack_gossip_announce(0, 540, 'p2p is very cool!')
    packing.send_msg(sock, values['code'], values['data'])
    sock.close()
    print('500 sent')
    time.sleep(2)

    print('Sending 501')
    sock = socket.socket()
    sock.connect((ip_address, port))
    values = packing.pack_gossip_notify(540)
    packing.send_msg(sock, values['code'], values['data'])
    sock.close()
    print('501 sent')
    time.sleep(2)

    print('Sending 502')
    sock = socket.socket()
    sock.connect((ip_address, port))
    values = packing.pack_gossip_notification(1, 540, 'p2p is very cool!')
    packing.send_msg(sock, values['code'], values['data'])
    sock.close()
    print('502 sent')
    time.sleep(2)

    print('Sending 503')
    sock = socket.socket()
    sock.connect((ip_address, port))
    values = packing.pack_gossip_validation(1, 1)
    packing.send_msg(sock, values['code'], values['data'])
    sock.close()
    print('503 sent')
    time.sleep(2)

    print('Sending 510')
    sock = socket.socket()
    sock.connect((ip_address, port))
    values = packing.pack_gossip_peer_request()
    packing.send_msg(sock, values['code'], values['data'])
    sock.close()
    print('510 sent')
    time.sleep(2)

    print('Sending 511')
    sock = socket.socket()
    values = packing.pack_gossip_peer_response({'1.1.1.1:1': None, '2.2.2.2:2': None, '3.3.3.3:3': None})
    sock.connect((ip_address, port))
    packing.send_msg(sock, values['code'], values['data'])
    sock.close()
    print('511 sent')
    time.sleep(2)

    print('Sending 512')
    sock = socket.socket()
    sock.connect((ip_address, port))
    values = packing.pack_gossip_peer_update('127.0.0.1', 2222, 0, 1)
    packing.send_msg(sock, values['code'], values['data'])
    sock.close()
    print('512 sent')

except Exception as e:
    print("connection error: {0}".format(e))
