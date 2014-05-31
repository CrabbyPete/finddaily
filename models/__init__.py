from config import MONGODB

from mongoengine import connect
try:
    connect(MONGODB['db'], **MONGODB['options'] )
except:
    pass
