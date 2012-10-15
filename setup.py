import os
from distutils.core import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "parseltone",
    version = "0.0.1",
    author = "Izeni, Inc.",
    author_email = "contact+parseltone@izeni.com",
    description = ("Framework and tools for interfacing with FreeSWITCH."),
    license = "MPL",
    keywords = "freeswitch telephony",
    url = "http://parseltone.org",
    packages=[
        'parseltone',
        'parseltone.api',
        'parseltone.django',
        'parseltone.django.apps.api',
        'parseltone.django.apps.freeswitch',
        'parseltone.django.apps.freeswitch.models',
        'parseltone.django.apps.honeylog',
        'parseltone.django.apps.provisioning',
        'parseltone.django.apps.provisioning.polycom',
        'parseltone.eventsocket',
        'parseltone.interface',
        'parseltone.interface.client',
        'parseltone.interface.client.curses',
        'parseltone.interface.client.pyqt',
        'parseltone.interface.manager',
        'parseltone.interface.manager.avatar',
        'parseltone.interface.manager.checkers',
        'parseltone.utils',
    ],
    package_data={
        'parseltone.django.apps.freeswitch': [
            'fixtures/*',
            'templates/freeswitch/*.xml',
            'templates/freeswitch/confs/*.xml',
        ],
        'parseltone.django.apps.provisioning': [
            'templates/provisioning/polycom/*.xml',
        ],
    },
    install_requires=['urwid', 'twisted'],
    scripts=['parseltone/tools/pt_cli'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Communications :: Telephony",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
    ],
)
