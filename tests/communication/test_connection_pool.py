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

from gossip.communication.connection import GossipConnectionPool

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class MockedConnection:
    def __init__(self, name):
        self.name = name

    def close(self):
        pass

    def shutdown(self, arg):
        pass


class TestConnectionPool(unittest.TestCase):
    """
    Test class for ConnectionPool class
    """

    def test_maintain_connections_list(self):
        """
            This test method adds up to four connections to a pool with a maximum size of 3
            It fails if after adding the fourth connection, the connection pool is larger than 3 and
            if any other connection, instead of the first one that has been added, was removed
            :return: None
        """
        max_pool_size = 3
        connection_list = GossipConnectionPool('TestPool', max_pool_size)

        connection_list.add_connection('127.0.0.1:2', MockedConnection('DummyConnection2'))
        connection_list.add_connection('127.0.0.1:1', MockedConnection('DummyConnection1'))

        pool_size = len(connection_list._connections)
        assert pool_size == 2, "expected pool size to be %s but was %s" % (max_pool_size, pool_size)

        connection_list.add_connection('127.0.0.1:3', MockedConnection('DummyConnection3'))
        connection_list.add_connection('127.0.0.1:0', MockedConnection('DummyConnection0'))

        pool_size = len(connection_list._connections)
        assert pool_size == max_pool_size, "expected pool size to be %s but was %s" % (max_pool_size, pool_size)

