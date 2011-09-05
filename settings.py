import os

CHARGIFY_API_KEY = 'xxXPsiW-FGTHA6STZ6P0'
AWS_ACCESS_KEY_ID = '0Z67F08VD9JMM1WKRDR2'
AWS_SECRET_ACCESS_KEY = 'g6o8NjU3ClIYJmaGurL+sKctlQrpEUF6irQyrpPX'
BUCKET_NAME = 'sharedocapp' # An AWS account can only have 100 buckets, so everybody is gonna share this bucket!
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB_NAME = 'dev'
DIRNAME = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_PATHS = [os.path.join(DIRNAME,'views')]
EMAIL_BOX_NAME = ''
EMAIL_BOX_PWD = ''
EMAIL_SMTP_HOST = 'localhost'
EMAIL_FROM_ADDR = 'robot@piles.io'

try:
	from local_settings import *
except ImportError:
	pass # It's cool if there's no local_Settings module