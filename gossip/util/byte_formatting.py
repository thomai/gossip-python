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

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


def short_to_bytes(short_value):
    """
    Transforms a short to a byte array (using Big-Endian!)

    :param short_value: Any integer that is greater than 0 and smaller than 65535
    :return: A bytes array with the highest byte at position 0 and the lowest at position 1
    """
    return bytes([int(short_value) >> 8]) + bytes([int(short_value) & 0xff])


def bytes_to_short(higher_byte, lower_byte):
    """
    Transforms two bytes into a short (Using Big-Endian!)

    :param higher_byte: The byte at position 0 (Higher byte)
    :param lower_byte: The byte at position 1 (Lower byte)
    :return: The two bytes transformed into a short
    """
    return (higher_byte << 8) | lower_byte
