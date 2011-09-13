import os

class Settings(object):
    def __init__(self):
        self.conf_set = set()
        self.confs = []
        self.ignores = []
        self.requires = []
        
    def ignore(self,conf_name):
        self.ignores.append(conf_name)
        
    def require(self,conf_name):
        self.requires.append(conf_name)
        
    def add_conf(self,conf,conf_name):
        if conf_name in self.conf_set:
            return
        self.conf_set.add(conf_name)
        self.confs.append((conf,conf_name))
    
    def __call__(self,name):
        for conf,conf_name in reversed(self.confs):
            if conf_name in self.ignores:
                continue
            if len(self.requires) > 0 and conf_name not in self.requires:
                continue
                
            if conf.get(name,None) is not None:
                return conf[name]
        raise AttributeError
settings = Settings()



settings.add_conf({

'DIRNAME': os.path.abspath(os.path.dirname(__file__)),

### API Keys
'CHARGIFY_API_KEY': 'xxXPsiW-FGTHA6STZ6P0',
'AWS_ACCESS_KEY_ID': '0Z67F08VD9JMM1WKRDR2',
'AWS_SECRET_ACCESS_KEY': 'g6o8NjU3ClIYJmaGurL+sKctlQrpEUF6irQyrpPX',

### App settings
# The name of the S3 bucket where the application's user content and static files will live
'APP_BUCKET': 'dev.piles.io',
# The default Access Control setting for new files
'APP_BUCKET_ACL': 'private', #'bucket-owner-full-control'
# Bucket where logs are stored
'LOG_BUCKET': 'dev.piles.io-logging',
# Prefixed before all logs delivered to the above log bucket
'LOG_BUCKET_PREFIX': 'dev.piles.io-access-log-',

'FILE_POST_URL': 'http://dev.piles.io',
# The domain on which the application logic and API lives
'APP_DOMAIN': 'api.dev.piles.io',
# The domain on which the application and user content lives
'CONTENT_DOMAIN': 'dev.piles.io',

### Database settings
'MONGO_HOST': 'localhost',
'MONGO_PORT': 27017,
'MONGO_DB_NAME': 'piles-dev',

### Framework settings
'TEMPLATE_PATHS': [os.path.join(os.path.abspath(os.path.dirname(__file__)),'views')],

### Email settings
'EMAIL_BOX_NAME': '',
'EMAIL_BOX_PWD': '',
'EMAIL_SMTP_HOST': 'localhost',
'EMAIL_FROM_ADDR': 'robot@piles.io',

'DEPLOYED': False, # This should be true in the `local_settings.py` file of the API server


},'global')

    

try:
	from local_settings import conf
	settings.add_conf(conf,'local')
except ImportError:
	pass # It's cool if there's no local_Settings module