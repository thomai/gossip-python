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

from gossip.util import byte_formatting

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


def test_short_to_bytes():
    short_first = 65535
    short_second = 0
    short_third = 3999
    short_fourth = 255
    sf_bytes = byte_formatting.short_to_bytes(short_first)
    assert sf_bytes[0] == 0xff
    assert sf_bytes[1] == 0xff

    ss_bytes = byte_formatting.short_to_bytes(short_second)
    assert ss_bytes[0] == 0x00
    assert ss_bytes[1] == 0x00

    st_bytes = byte_formatting.short_to_bytes(short_third)
    assert st_bytes[0] == 0x0F
    assert st_bytes[1] == 0x9F

    sfo_bytes = byte_formatting.short_to_bytes(short_fourth)
    assert sfo_bytes[0] == 0x00
    assert sfo_bytes[1] == 0xff


def test_bytes_to_short():
    short_first = byte_formatting.bytes_to_short(0xff, 0xff)
    short_second = byte_formatting.bytes_to_short(0x00, 0x00)
    short_third = byte_formatting.bytes_to_short(0x0f, 0x9f)
    short_fourth = byte_formatting.bytes_to_short(0x00, 0xff)
    assert short_first == 65535
    assert short_second == 0
    assert short_third == 3999
    assert short_fourth == 255