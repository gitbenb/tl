# tl/path.py
#
#

""" module to include this bot into the python path. """

import warnings
warnings.simplefilter("ignore")

import os, sys
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.getcwd() + os.sep + "..")
