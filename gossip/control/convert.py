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

from gossip.util.packing import pack_gossip_notification
from gossip.util.message import MessageGossipNotification

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


def from_announce_to_notification(msg_id, message):
    """
    Method by which the values of an announce message are transferred into a notification message

    :param msg_id: the message id of the new notification message
    :param message: the message to convert
    :return: the packed converted message object
    """
    message_values = message.get_values()
    msg_data = pack_gossip_notification(msg_id, message_values['type'], message_values['message'])['data']
    return MessageGossipNotification(msg_data)
