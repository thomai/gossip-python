# Copyright 2016 Anselm Binninger, Thomas Maier, Ralph Schaumann
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='gossip-python',
    version='0.0.1',
    description='Python module for gossip integration',
    long_description=readme,
    author='Anselm Binninger | Ralph Oliver Schaumann | Thomas Maier',
    author_email='anselm.binninger@tum.de | tom.maier@tum.de',
    url='https://stash.bwk-technik.de/projects/PTP/repos/p2p-code/',
    download_url='https://bwk-software.com/builds/gossip/downloads/0.0.1',
    keywords=['gossip','gossip-python','peertopeer','p2p'],
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    data_files=[('', ['LICENSE'])]
)