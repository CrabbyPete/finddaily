import os
import logging
import inspect

from logging.handlers import SMTPHandler

from flask            import *

def log( msg ):
    stack = inspect.stack()[1]
    file = os.path.basename( stack[1] ) 
    print 'Error: {} @ {}:{}'.format (msg, file, stack[2] ) 
    