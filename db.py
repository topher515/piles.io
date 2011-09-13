from settings import MONGO_HOST, MONGO_PORT, MONGO_DB_NAME
from pymongo import Connection, ASCENDING, DESCENDING
db = Connection(MONGO_HOST, MONGO_PORT)[MONGO_DB_NAME]
print "Connected to %s:%s db:%s" % (MONGO_HOST, MONGO_PORT, MONGO_DB_NAME)

def reset_db():
	if raw_input('Do you really want to DROP the database "%s" [type yes]?' % db.name) == 'yes':
		db.dropDatabase()
		db.invites.save({'code':'gregsucks','remaining':100})
