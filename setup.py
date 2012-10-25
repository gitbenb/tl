#!/usr/bin/env python3
#
#

target = "tl" 

import os
import sys

if sys.version_info.major < 3: print("you need to run this python3 distribute_setup.py first") ; os._exit(1)

upload = []


try:
    from distribute_setup import use_setuptools
    use_setuptools()
except Exception as ex: print("you need to run this python3 distribute_setup.py first: %s" % str(ex)) ; os._exit(1)

try: 
   from setuptools import setup
except Exception as ex: print("i need setuptools to properly install TIMELINE") ; os._exit(1)

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir): print("%s does not exist" % dir) ; os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc"):
                continue
            upl.append(d)
    return upl

def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc"):
                continue
            upl.append(d)

    return upl

from tl.version import __version__

setup(
    name='tl',
    version='%s' % __version__,
    url='https://github.com/feedbackflow/tl',
    author='Bart Thate',
    author_email='feedbackflow@gmail.com',
    description='The Timeline Bot',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    scripts=['bin/tl',
             'bin/tl-fleet',
             'bin/tl-irc',
             'bin/tl-sleek',
            ],
    packages=['tl',
              'tl.db',
              'tl.api',
              'tl.tornado',
              'tl.drivers',
              'tl.drivers.console',
              'tl.drivers.irc',
              'tl.drivers.sleek',
              'tl.drivers.tornado',
              'tl.drivers.twitter',
              'tl.examples',
              'tl.lib', 
              'tl.utils',
              'tl.plugs',
              'tl.plugs.db',
              'tl.plugs.core',
              'tl.plugs.extra',
              'tl.plugs.timeline',
              'tl.contrib',
              'tl.contrib.natural',
              'tl.contrib.natural.templatetags',
              'tl.contrib.bs4',
              'tl.contrib.bs4.builder',
              'tl.contrib.tornado',
              'tl.contrib.tornado.platform',
              'tl.contrib.tweepy',
              'tl/contrib/sleekxmpp',
              'tl/contrib/sleekxmpp/stanza',   
              'tl/contrib/sleekxmpp/test',     
              'tl/contrib/sleekxmpp/roster',   
              'tl/contrib/sleekxmpp/xmlstream',
              'tl/contrib/sleekxmpp/xmlstream/matcher',
              'tl/contrib/sleekxmpp/xmlstream/handler',
              'tl/contrib/sleekxmpp/plugins',
              'tl/contrib/sleekxmpp/plugins/xep_0004',
              'tl/contrib/sleekxmpp/plugins/xep_0004/stanza',
              'tl/contrib/sleekxmpp/plugins/xep_0009',
              'tl/contrib/sleekxmpp/plugins/xep_0009/stanza',
              'tl/contrib/sleekxmpp/plugins/xep_0030',
              'tl/contrib/sleekxmpp/plugins/xep_0030/stanza',
              'tl/contrib/sleekxmpp/plugins/xep_0050',
              'tl/contrib/sleekxmpp/plugins/xep_0059',
              'tl/contrib/sleekxmpp/plugins/xep_0060',
              'tl/contrib/sleekxmpp/plugins/xep_0060/stanza',
              'tl/contrib/sleekxmpp/plugins/xep_0066',
              'tl/contrib/sleekxmpp/plugins/xep_0078',
              'tl/contrib/sleekxmpp/plugins/xep_0085',
              'tl/contrib/sleekxmpp/plugins/xep_0086',
              'tl/contrib/sleekxmpp/plugins/xep_0092',
              'tl/contrib/sleekxmpp/plugins/xep_0128',
              'tl/contrib/sleekxmpp/plugins/xep_0199',
              'tl/contrib/sleekxmpp/plugins/xep_0202',
              'tl/contrib/sleekxmpp/plugins/xep_0203',
              'tl/contrib/sleekxmpp/plugins/xep_0224',
              'tl/contrib/sleekxmpp/plugins/xep_0249',
              'tl/contrib/sleekxmpp/features',
              'tl/contrib/sleekxmpp/features/feature_mechanisms',
              'tl/contrib/sleekxmpp/features/feature_mechanisms/stanza',
              'tl/contrib/sleekxmpp/features/feature_starttls',
              'tl/contrib/sleekxmpp/features/feature_bind',   
              'tl/contrib/sleekxmpp/features/feature_session',
              'tl/contrib/sleekxmpp/thirdparty',
              'tl/contrib/sleekxmpp/thirdparty/suelta',
              'tl/contrib/sleekxmpp/thirdparty/suelta/mechanisms',
           ],
    long_description = """ The Timeline Bot -  https://github.com/feedbackflow/tl """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    data_files=[(target + os.sep + 'examples', uploadfiles('tl' + os.sep + 'examples')),
                (target + os.sep + 'data', uploadfiles('tl' + os.sep + 'data')),
                (target + os.sep + 'data' + os.sep + 'static', uploadlist('tl' + os.sep + 'data' + os.sep + 'static')),
                (target + os.sep + 'data' + os.sep + 'templates', uploadlist('tl' + os.sep + 'data' + os.sep + 'templates'))],
    package_data={'': ["*.example"],
                 },
)
