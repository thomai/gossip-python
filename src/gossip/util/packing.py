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
import struct

from gossip.util.exceptions import GossipMessageException, GossipClientDisconnectedException
from gossip.util.message_code import MESSAGE_CODE_ANNOUNCE, MESSAGE_CODE_PEER_REQUEST, MESSAGE_CODE_PEER_RESPONSE, \
    MESSAGE_CODE_NOTIFICATION, MESSAGE_CODE_NOTIFY, MESSAGE_CODE_PEER_UPDATE, MESSAGE_CODE_VALIDATION, \
    MESSAGE_CODE_GOSSIP_MAX, MESSAGE_CODE_GOSSIP_MIN, MESSAGE_CODE_PEER_INIT
from gossip.util.byte_formatting import bytes_to_short, short_to_bytes

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


def pack_gossip_announce(ttl, data_type, msg_data):
    """
    Method by which a message of type 'GOSSIP ANNOUNCE' is packed/encoded

    :param ttl: the time to live
    :param data_type: the data type of the message
    :param msg_data: the data to pack
    :return: dict, code and data
    """
    if ttl >= 0xff:
        raise ValueError('TTL may not be larger than 1 byte')
    # encode the ttl
    b_ttl = bytes([ttl])
    # reserved byte
    b_reserved = bytes([0])
    b_type = short_to_bytes(data_type)
    data = b''
    for i in list(msg_data):
        data += bytes([int(i)])
    return {'code': MESSAGE_CODE_ANNOUNCE, 'data': b_ttl + b_reserved + b_type + data}


def pack_gossip_notify(data_type):
    """
    Method by which a message of type 'GOSSIP NOTIFY' is packed/encoded

    :param data_type: the data type of the message
    :return: dict, code and data
    """
    # reserved byte
    b_reserved = bytes([0])
    b_type = short_to_bytes(data_type)
    return {'code': MESSAGE_CODE_NOTIFY, 'data': b_reserved + b_reserved + b_type}


def pack_gossip_notification(msg_id, data_type, msg_data):
    """
    Method by which a message of type 'GOSSIP NOTIFICATION' is packed/encoded

    :param msg_id: the id of the message
    :param data_type: the data type of the message
    :param msg_data: the data to pack
    :return: dict, code and data
    """
    b_type = short_to_bytes(data_type)
    b_msg_id = short_to_bytes(msg_id)

    data = b''
    for i in list(msg_data):
        data += bytes([int(i)])
    return {'code': MESSAGE_CODE_NOTIFICATION, 'data': b_msg_id + b_type + data}


def pack_gossip_validation(msg_id, valid_bit):
    """
    Method by which a message of type 'GOSSIP VALIDATION' is packed/encoded

    :param msg_id: the id of the message
    :param valid_bit: set iff valid, unset else
        value may be 0 or 1
    :return: dict, code and data
    """
    b_msg_id = short_to_bytes(msg_id)
    if valid_bit == 0:
        b_valid_bit = b'\x00'
    elif valid_bit == 1:
        b_valid_bit = b'\x01'
    else:
        raise ValueError('Valid bit may only be 1 or 0')
    return {'code': MESSAGE_CODE_VALIDATION, 'data': b_msg_id + bytes([0]) + b_valid_bit}


def pack_gossip_peer_request(address_port):
    """
    Method by which a message of type MESSAGE_CODE_PEER_REQUEST is packed/encoded

    :return: dict, code and data
    """
    address, port = address_port.split(':')
    ipv4_part_1, ipv4_part_2, ipv4_part_3, ipv4_part_4 = address.split('.')
    b_address = bytes([int(ipv4_part_1)]) + bytes([int(ipv4_part_2)]) + bytes([int(ipv4_part_3)]) + bytes(
        [int(ipv4_part_4)])
    b_port = short_to_bytes(port)
    b_reserved = b'\x00'
    return {'code': MESSAGE_CODE_PEER_REQUEST, 'data': b_address + b_port + b_reserved + b_reserved}


def pack_gossip_peer_response(local_connections):
    """
    Method by which a message of type MESSAGE_CODE_PEER_RESPONSE is packed/encoded

    :param local_connections: list with all local connections
    :return: dict with format {'code': <message_code>, 'data': <data>}
    """
    b_connections = b''
    for key in local_connections:
        address, port = key.split(':')
        ipv4_part_1, ipv4_part_2, ipv4_part_3, ipv4_part_4 = address.split('.')
        b_address = bytes([int(ipv4_part_1)]) + bytes([int(ipv4_part_2)]) + bytes([int(ipv4_part_3)]) + bytes(
            [int(ipv4_part_4)])
        b_port = short_to_bytes(port)
        b_connections += b_address + b_port

    return {'code': MESSAGE_CODE_PEER_RESPONSE, 'data': b_connections}


PEER_UPDATE_TYPE_PEER_LOST = 0
PEER_UPDATE_TYPE_PEER_FOUND = 1


def pack_gossip_peer_update(identifier, ttl, update_type):
    """
    Method by which a message of type MESSAGE_CODE_PEER_UPDATE is packed/encoded

    :return: dict, code and data
    """
    address, port = identifier.split(':')
    ipv4_part_1, ipv4_part_2, ipv4_part_3, ipv4_part_4 = address.split('.')
    b_address = bytes([int(ipv4_part_1)]) + bytes([int(ipv4_part_2)]) + bytes([int(ipv4_part_3)]) + bytes(
        [int(ipv4_part_4)])
    b_port = short_to_bytes(port)
    b_ttl = bytes([(int(ttl) & 0xff)])
    if update_type == PEER_UPDATE_TYPE_PEER_LOST:
        b_update = b'\x00'
    elif update_type == PEER_UPDATE_TYPE_PEER_FOUND:
        b_update = b'\x01'
    else:
        raise ValueError('update type may only be 0 or 1')
    return {'code': MESSAGE_CODE_PEER_UPDATE, 'data': b_address + b_port + b_ttl + b_update}


def pack_gossip_peer_init(identifier):
    """
    Method by which a message of type MESSAGE_CODE_PEER_INIT is packed/encoded

    :return: dict, code and data
    """
    address, port = identifier.split(':')
    ipv4_part_1, ipv4_part_2, ipv4_part_3, ipv4_part_4 = address.split('.')
    b_address = bytes([int(ipv4_part_1)]) + bytes([int(ipv4_part_2)]) + bytes([int(ipv4_part_3)]) + bytes(
        [int(ipv4_part_4)])
    b_port = short_to_bytes(port)

    return {'code': MESSAGE_CODE_PEER_INIT, 'data': b_address + b_port}


def pack_message_other(code, data):
    """
    Method by which other modules messages are (re-)packed

    :param code: the code of the message
    :param data: the data to pack
    :return: dict, code and data
    """
    b_data = bytes(data, 'ascii')
    return {'code': code, 'data': b_data}


def send_msg(sock, code, msg):
    """
    Method by which a Message is encoded and sent

    :param sock: the socket to send the message on
    :param code: the code of the message
    :param msg: the message to encode
    """
    # the size of the message is size of the code to send + 4 bytes
    size = len(msg) + 4
    # encode the size into two bytes
    b_size = short_to_bytes(size)
    # encode the message code into two bytes
    b_code = short_to_bytes(code)
    # add all the bytes up to construct the message
    b_msg = b_size + b_code + msg
    # send everything
    logging.info('Send message: %d | %d | %s' % (size, code, msg))
    sock.send(b_msg)


def receive_msg(sock):
    """
    Method by which a byte message is decoded

    :param sock: tcp socket to read from
    :return: a dict of the decoded values
    """
    msg_hdr = sock.recv(4)
    if len(msg_hdr) == 0:
        raise GossipClientDisconnectedException('Client disconnected')
    elif len(msg_hdr) < 4:
        raise GossipMessageException('Invalid header (< 4)')
    # the first and the second byte encode the message length
    size_fst, size_snd = struct.unpack('{}B'.format(2), msg_hdr[:2])
    size = bytes_to_short(size_fst, size_snd)
    if size < 4:
        raise GossipMessageException('Invalid size (< 4)')
    # third and forth byte encode the message code
    msg_code_fst, msg_code_snd = struct.unpack('{}B'.format(2), msg_hdr[2:4])
    code = bytes_to_short(msg_code_fst, msg_code_snd)
    if not MESSAGE_CODE_GOSSIP_MIN <= code < MESSAGE_CODE_GOSSIP_MAX:
        raise GossipMessageException('Invalid message code')
    data = sock.recv(size - 4)
    logging.info('Received message: %d | %d | %s' % (size, code, data))
    msg = {'size': size, 'code': code, 'message': data}
    return msg
