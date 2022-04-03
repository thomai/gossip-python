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
import os


with open('README.rst', 'r', encoding='utf8') as f:
    readme = f.read()

with open('LICENSE', 'r', encoding='utf8') as f:
    license = f.read()

with open('requirements-test.txt', 'r', encoding='utf8') as f:
    requirements_test = f.readlines()

with open('requirements-doc.txt', 'r', encoding='utf8') as f:
    requirements_doc = f.readlines()


with open('requirements-sim.txt', 'r', encoding='utf8') as f:
    requirements_sim = f.readlines()

scripts = [os.path.join('src/gossip/examples', example_file) \
           for example_file in os.listdir('src/gossip/examples')]

setup(
    name='gossip-python',
    version='0.0.2',
    description='Python module for gossip integration',
    long_description=readme,
    author='Anselm Binninger | Ralph Oliver Schaumann | Thomas Maier',
    author_email='anselm.binninger@tum.de | tom.maier@tum.de',
    url='https://stash.bwk-technik.de/projects/PTP/repos/p2p-code/',
    download_url='https://bwk-software.com/builds/gossip/downloads/0.0.1',
    keywords=['gossip','gossip-python','peertopeer','p2p'],
    license=license,
    extras_require={
        'test': requirements_test,
        'doc': requirements_doc,
        'sim': requirements_sim
    },
    entry_points={
        'console_scripts': [
            "gossip=gossip.gossip_main:main"
        ]
    },
    python_requires='>=3.6',
    package_dir={"": "src"},
    packages=find_packages('src'),
    package_data={
        'gossip': ['LICENSE', 'config/*.ini']
    },
    scripts=scripts
)
