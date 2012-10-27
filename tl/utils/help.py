# tl/utils/help.py
#
#

""" tl helper functions. """

## basic imports

import io

## cstr class

class cstr(str): pass

## cbytes class

class cbytes(bytes): pass

## istr class

class istr(io.StringIO): pass

## ibytes class

class ibytes(io.BytesIO): pass
    