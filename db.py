from settings import MONGO_HOST, MONGO_PORT, MONGO_DB_NAME
from pymongo import Connection
db = Connection(MONGO_HOST, MONGO_PORT)[MONGO_DB_NAME]