# tl/utils/resolve.py
#
#

""" host resolver. """

## basic imports

import socket

## resolve_host function

def resolve_host(timeout=1.0):
    oldtimeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try: hn = socket.gethostname()
    except socket.timeout: hn = None
    socket.setdefaulttimeout(oldtimeout)
    return hn

## resolve_ip function

def resolve_ip(hostname=None, timeout=1.0):
    oldtimeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try: ip = socket.gethostbyname(hostname or socket.gethostname())
    except socket.timeout: ip = None
    socket.setdefaulttimeout(oldtimeout)
    return ip
    