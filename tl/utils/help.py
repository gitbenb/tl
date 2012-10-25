# tl/utils/help.py
#
#

""" tl helper functions. """

## basic imports

import io

## cstr class

class cstr(str): pass


## istr class

class istr(io.StringIO):

    """ istr is a stream of chars. """

    pass

class ibytes(io.BytesIO):

    """ ibytes is a stream of bytes. """

    pass
    