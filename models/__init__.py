from config import MONGODB
from pymongo import ReadPreference

from mongoengine import connect
connect('finddaily', host ='mongodb://coachpete:mrS0fty@ds031213.mongolab.com:31213/finddaily', read_preference=ReadPreference.PRIMARY)
