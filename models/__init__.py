from config import MONGODB

from mongoengine import connect
connect(MONGODB['db'], **MONGODB['options'] )
