# tl/utils/popen.py
#
#

""" popen helper functions. """

## defines

go = False

## basic imports

try:
    from subprocess import Popen, PIPE
    from .locking import lockdec
    import _thread, io, logging, types
    go = True
except: go = False

if go:

    ## locks

    popenlock = _thread.allocate_lock()
    popenlocked = lockdec(popenlock)

    ## exceptions

    class PopenWhitelistError(Exception):

        def __init__(self, item):
            Exception.__init__(self)
            self.item = item
        
        def __str__(self):
            return self.item

    class PopenListError(Exception):

        def __init__(self, item):
            Exception.__init__(self)
            self.item = item
        
        def __str__(self):
            return str(self.item)

    ## _Popen4 class

    class _Popen4(Popen):

        """ extend the builtin Popen class with a close method. """

        def __init__(self, args):
            Popen.__init__(self, args, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            self.fromchild = self.stdout
            self.tochild   = self.stdin
            self.errors    = self.stderr

        def close(self):
            """ shutdown. """
            self.wait()
            try: self.stdin.close()
            except: pass
            try: self.stdout.close()
            except: pass
            try: self.errors.close()
            except: pass
            return self.returncode

    ## _popen function

    def _popen(args, userargs=[]):
        """ do the actual popen .. make sure the arguments are passed on as list. """
        if type(args) != list: raise PopenListError(args)
        if type(userargs) != list: raise PopenListError(args)
        for i in userargs:
            if i.startswith('-'): raise PopenWhitelistError(i)
        proces = _Popen4(args + userargs)
        return proces
