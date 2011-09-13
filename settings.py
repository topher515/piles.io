import os
DIRNAME = os.path.abspath(os.path.dirname(__file__))

### API Keys
CHARGIFY_API_KEY = 'xxXPsiW-FGTHA6STZ6P0'
AWS_ACCESS_KEY_ID = '0Z67F08VD9JMM1WKRDR2'
AWS_SECRET_ACCESS_KEY = 'g6o8NjU3ClIYJmaGurL+sKctlQrpEUF6irQyrpPX'

### App settings
# The name of the S3 bucket where the application's user content and static files will live
APP_BUCKET = 'dev.piles.io'
# The default Access Control setting for new files
APP_BUCKET_ACL = 'private' #'bucket-owner-full-control'
# Bucket where logs are stored
LOG_BUCKET = 'dev.piles.io-logging'
# Prefixed before all logs delivered to the above log bucket
LOG_BUCKET_PREFIX = 'dev.piles.io-access-log-'

FILE_POST_URL = 'http://dev.piles.io'
# The domain on which the application logic and API lives
APP_DOMAIN = 'api.dev.piles.io'
# The domain on which the application and user content lives
CONTENT_DOMAIN = 'dev.piles.io'

### Database settings
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB_NAME = 'piles-dev'

### Framework settings
TEMPLATE_PATHS = [os.path.join(DIRNAME,'views')]

### Email settings
EMAIL_BOX_NAME = ''
EMAIL_BOX_PWD = ''
EMAIL_SMTP_HOST = 'localhost'
EMAIL_FROM_ADDR = 'robot@piles.io'

try:
	from local_settings import *
except ImportError:
	pass # It's cool if there's no local_Settings module