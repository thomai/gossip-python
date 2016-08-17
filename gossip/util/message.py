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

import struct
from abc import ABCMeta

from gossip.util.message_code import MESSAGE_CODE_ANNOUNCE, MESSAGE_CODE_PEER_REQUEST, MESSAGE_CODE_PEER_RESPONSE, \
    MESSAGE_CODE_NOTIFICATION, MESSAGE_CODE_NOTIFY, MESSAGE_CODE_PEER_UPDATE, MESSAGE_CODE_VALIDATION, \
    MESSAGE_CODE_PEER_INIT

from gossip.util.byte_formatting import short_to_bytes, bytes_to_short

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class MessageGossip:
    """
        Baseclass for gossip messages
    """

    __metaclass__ = ABCMeta

    def __init__(self, code, data):
        """
        C'tor

        :param code: the code of this message
        """
        self.code = code
        self.data = data

    def get_code(self):
        """
        Method by which the code of this message is retrieved

        :return: the code of this message
        """
        return self.code

    def get_values(self):
        """
        Method by which the values of this message are retrieved

        :return: the values of this message
        """
        pass

    def __str__(self):
        """
        to string method

        :return: a string representation of this message
        """
        return '%s' % self.get_values()

    def encode(self):
        """
        Encodes this message into a byte array

        :return: a byte array with the encoded header and payload
        """
        size = len(self.data) + 4
        # encode the size into two bytes
        b_size = short_to_bytes(size)
        # encode the message code into two bytes
        b_code = short_to_bytes(self.code)
        # add all the bytes up to construct the message
        b_msg = b_size + b_code + self.data
        return b_msg


class MessageGossip51x(MessageGossip):
    """
    Baseclass for gossip messages of code 510-519
    """

    def __init__(self, code, data):
        """
        C'Tor

        :param code: the code of this message
        """
        super().__init__(code, data)


class MessageOther:
    """
    If a message can't be decoded properly a MessageOther will be returned.
    """

    def __init__(self, message_code, message_data):
        """
        C'Tor

        :param message_code: the code of the message
        :param message_data: the data of the message
        """
        self.code = message_code
        self.data = message_data

    def get_values(self):
        """
        Method by which the values of this message are retrieved

        :return: a dictionary with the values of this message (keys: code, message)
        """
        return {'code': self.code, 'message': self.data}

    def encode(self):
        size = len(self.data) + 4
        # encode the size into two bytes
        b_size = short_to_bytes(size)
        b_code = short_to_bytes(self.code)
        # add all the bytes up to construct the message
        b_msg = b_size + b_code + self.data
        return b_msg

    def __str__(self):
        """
        to string method

        :return: a string representation of this message
        """
        return {'code': self.code, 'data': self.data}.__str__()


class MessageGossipAnnounce(MessageGossip):
    """
    GossipAnnounceMessage
    This messages are received from api connections. If you want to implement an api client for gossip
    its messages need to be structured like that
    """

    def __init__(self, data):
        """
        C'Tor

        :param bytes data: the data of the message
        """
        super().__init__(MESSAGE_CODE_ANNOUNCE, data)
        self.ttl = struct.unpack('{}B'.format(1), data[:1])[0]
        data_type_fst, data_type_snd = struct.unpack('{}B'.format(2), data[2:4])
        self.data_type = bytes_to_short(data_type_fst, data_type_snd)
        self.msg = struct.unpack('{}B'.format(len(data) - 4), data[4:len(data)])

    def get_values(self):
        """
        Method by which the values of this message are retrieved

        :return: a dictionary with the values of this message (keys: code, message, TTL, type)
        """
        return {'message': self.msg, 'code': self.code, 'TTL': self.ttl, 'type': self.data_type}

    def __hash__(self):
        return hash((self.msg, self.code, self.data_type))

    def __eq__(self, other):
        return (self.msg, self.code, self.data_type) == (other.msg, other.code, other.data_type)

    def __ne__(self, other):
        return not (self == other)


class MessageGossipNotify(MessageGossip):
    """
    This message is sent from the gossip instance to all apis that registered for this specific datatype
    An api client needs to implement this messageformat
    """

    def __init__(self, data):
        """
        C'Tor

        :param bytes data: the data of the message
        """
        super().__init__(MESSAGE_CODE_NOTIFY, data)
        data_type_fst, data_type_snd = struct.unpack('{}B'.format(2), data[2:4])
        self.data_type = bytes_to_short(data_type_fst, data_type_snd)

    def get_values(self):
        """
        Method by which the values of this message are retrieved

        :return: a dictionary with the values of this message (keys: code, type)
        """
        return {'type': self.data_type, 'code': self.code}


class MessageGossipNotification(MessageGossip):
    """
        Message that is sent from gossip to api clients which was received from other peers
    """

    def __init__(self, data):
        """
        C'Tor

        :param bytes data: the data from this message
        """
        super().__init__(MESSAGE_CODE_NOTIFICATION, data)
        msg_id_fst, msg_id_snd = struct.unpack('{}B'.format(2), data[:2])
        self.msg_id = bytes_to_short(msg_id_fst, msg_id_snd)
        data_type_fst, data_type_snd = struct.unpack('{}B'.format(2), data[2:4])
        self.data_type = bytes_to_short(data_type_fst, data_type_snd)
        self.msg = struct.unpack('{}B'.format(len(data) - 4), data[4:len(data)])

    def get_values(self):
        """
        Method by which the values of this message are retrieved

        :return: a dictionary with the values of this message (keys: code, type, id, message)
        """
        return {'id': self.msg_id, 'type': self.data_type, 'code': self.code, 'message': self.msg}


class MessageGossipValidation(MessageGossip):
    """
        Message that is sent from gossip to api clients to know whether or not a received message is valid
    """

    def __init__(self, data):
        """
        C'Tor

        :param data: the data from this message
        """
        super().__init__(MESSAGE_CODE_VALIDATION, data)
        msg_id_fst, msg_id_snd = struct.unpack('{}B'.format(2), data[:2])
        self.msg_id = bytes_to_short(msg_id_fst, msg_id_snd)
        _, valid = struct.unpack('{}B'.format(2), data[2:4])
        if valid == 0:
            self.valid = False
        else:
            self.valid = True

    def get_values(self):
        """
        Method by which the values of this message are retrieved

        :return: a dictionary with the values of this message (keys: id, valid, code)
        """
        return {'id': self.msg_id, 'valid': self.valid, 'code': self.code}


class MessageGossipPeerRequest(MessageGossip51x):
    """
        Message that is sent from one peer to another to get addresses of peers the other peer is connected to
    """

    def __init__(self, data):
        """
        C'Tor

        :param data: the data from this message
        """
        super().__init__(MESSAGE_CODE_PEER_REQUEST, data)
        self.data = data
        ipv4_part_1 = int(self.data[0])
        ipv4_part_2 = int(self.data[1])
        ipv4_part_3 = int(self.data[2])
        ipv4_part_4 = int(self.data[3])
        port = bytes_to_short(self.data[4], self.data[5])
        self.address = '%s.%s.%s.%s:%s' % (ipv4_part_1, ipv4_part_2, ipv4_part_3, ipv4_part_4, port)

    def get_values(self):
        return {'code': MESSAGE_CODE_PEER_REQUEST, 'p2p_server_address': self.address}


class MessageGossipPeerUpdate(MessageGossip51x):
    """
        Message that is sent recursively through the network as a respone to a new established connection
    """

    def __init__(self, data):
        """
        C'Tor

        :param data: the data from this message
        """
        super().__init__(MESSAGE_CODE_PEER_UPDATE, data)
        self.data = data
        ipv4_part_1 = int(self.data[0])
        ipv4_part_2 = int(self.data[1])
        ipv4_part_3 = int(self.data[2])
        ipv4_part_4 = int(self.data[3])
        port = bytes_to_short(self.data[4], self.data[5])
        self.address = '%s.%s.%s.%s:%s' % (ipv4_part_1, ipv4_part_2, ipv4_part_3, ipv4_part_4, port)
        self.ttl = int(self.data[6])
        self.update_type = int(self.data[7])

    def get_values(self):
        """
        Method by which the values of this message are retrieved

        :return: a dictionary with the values of this message (keys: code, address, ttl, update_type)
        """
        return {'code': MESSAGE_CODE_PEER_UPDATE, 'address': self.address, 'ttl': self.ttl,
                'update_type': self.update_type}

    def __hash__(self):
        return hash((self.address, self.update_type))

    def __eq__(self, other):
        return (self.address, self.update_type) == (other.address, other.update_type)

    def __ne__(self, other):
        return not (self == other)


class MessageGossipPeerResponse(MessageGossip51x):
    """
        Message that is sent as an answer to a previously sent peer request.
        It contains a list of server identifiers (address:port)
    """

    def __init__(self, data):
        """
        C'Tor

        :param data: the data from this message
        """
        super().__init__(MESSAGE_CODE_PEER_RESPONSE, data)
        self.data = data
        self.connections = []
        if len(self.data) > 0:
            data = struct.unpack('{}B'.format(len(self.data)), self.data)
            for i in range(0, len(self.data), 6):
                ipv4_part_1 = int(data[i])
                ipv4_part_2 = int(data[i + 1])
                ipv4_part_3 = int(data[i + 2])
                ipv4_part_4 = int(data[i + 3])
                port = bytes_to_short(self.data[i + 4], self.data[i + 5])
                address = '%s.%s.%s.%s:%s' % (ipv4_part_1, ipv4_part_2, ipv4_part_3, ipv4_part_4, port)
                self.connections.append(address)

    def get_values(self):
        """
        Method by which the values of this message are retrieved

        :return: a dictionary with the values of this message (keys: code, data)
        """
        return {'code': MESSAGE_CODE_PEER_RESPONSE, 'data': self.connections}


class MessageGossipPeerInit(MessageGossip51x):
    """
        Initial message that is sent from the connection peer to the remote peer
        to inform that peer about his server adderss (especially the port)
    """

    def __init__(self, data):
        """
        C'Tor

        :param data: the data from this message
        """
        super().__init__(MESSAGE_CODE_PEER_INIT, data)
        self.data = data
        ipv4_part_1 = int(self.data[0])
        ipv4_part_2 = int(self.data[1])
        ipv4_part_3 = int(self.data[2])
        ipv4_part_4 = int(self.data[3])
        port = bytes_to_short(self.data[4], self.data[5])
        self.address = '%s.%s.%s.%s:%s' % (ipv4_part_1, ipv4_part_2, ipv4_part_3, ipv4_part_4, port)

    def get_values(self):
        """
        Method by which the values of this message are retrieved

        :return: a dictionary with the values of this message (keys: code, p2p_server_address)
        """
        return {'code': MESSAGE_CODE_PEER_INIT, 'p2p_server_address': self.address}


""" Dictionary of all known message types within Gossip """
GOSSIP_MESSAGE_TYPES = {MESSAGE_CODE_ANNOUNCE: MessageGossipAnnounce,
                        MESSAGE_CODE_NOTIFY: MessageGossipNotify,
                        MESSAGE_CODE_NOTIFICATION: MessageGossipNotification,
                        MESSAGE_CODE_VALIDATION: MessageGossipValidation,
                        MESSAGE_CODE_PEER_REQUEST: MessageGossipPeerRequest,
                        MESSAGE_CODE_PEER_RESPONSE: MessageGossipPeerResponse,
                        MESSAGE_CODE_PEER_UPDATE: MessageGossipPeerUpdate,
                        MESSAGE_CODE_PEER_INIT: MessageGossipPeerInit}
