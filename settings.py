import os

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB_NAME = 'dev'
DIRNAME = os.path.abspath(os.path.dirname(__file__))

try:
	from local_settings import *
except ImportError:
	pass # It's cool if there's no local_Settings module