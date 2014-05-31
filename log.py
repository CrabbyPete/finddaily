import os
import logging
import inspect

from logging.handlers import SMTPHandler

from flask            import *
def init_logger( app ):
    pass

def log( msg ):
    stack = inspect.stack()[1]
    file = os.path.basename( stack[1] ) 
    msg =  'Error: {} @ {}:{}'.format (msg, file, stack[2] )
    print msg
    return msg 

