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

from multiprocessing import Manager

__author__ = 'Anselm Binninger, Thomas Maier, Ralph Schaumann'


class APIRegistrationHandler:
    """Thread-safe implementation of an handler for API registrations."""

    def __init__(self):
        """ Contructor. """
        self._api_registrations = Manager().dict()

    def register(self, code, identifier):
        """ Registers an identifier for a specified code.

        :param code: The code a particular identifier wants to register for
        :param identifier: The identifier who wants to register for the code
        """
        if code not in self._api_registrations.keys():
            self._api_registrations[code] = []

        if identifier not in self._api_registrations[code]:
            self._api_registrations[code] += [identifier]

    def unregister(self, identifier):
        """Removes a api from registrations

        :param identifier which should be removed from the registrations"""
        for code, registrations in self._api_registrations.items():
            if identifier in registrations:
                registrations.remove(identifier)
                self._api_registrations[code] = registrations

    def get_registrations(self, code):
        """ Provides all identifiers who registered for a specified code.

        :param code: The code for which the registrations are returned
        :returns: All identifiers who registered for this code
        """
        return self._api_registrations[code] if code in self._api_registrations else []
