import json
import datetime, base64, hmac, time
from urllib import quote as urlquote
from hashlib import sha1
from bottle import request, abort
import S3
from StringIO import StringIO
import logging
logger = logging.getLogger()

AWS_ACCESS_KEY_ID = '0Z67F08VD9JMM1WKRDR2'
AWS_SECRET_ACCESS_KEY = 'g6o8NjU3ClIYJmaGurL+sKctlQrpEUF6irQyrpPX'
BUCKET_NAME = 'sharedocapp' # An AWS account can only have 100 buckets, so everybody is gonna share this bucket!


# DEBUG
#AWS_SECRET_ACCESS_KEY = 'OtxrzxIsfpFjA7SwPzILwy8Bw21TLhquhboDYROV'
#AWS_ACCESS_KEY_ID = '44CF9590006BF252F707'

### Utils ###

## Auth
def session(request):
	return request.environ['beaker.session']
	
def logged_in(old_route):
	def new_route(*args,**kargs):
		if session(request).get('authenticated_as'):
			return old_route(*args,**kwargs)
		else:
			redirect('/login')
	return new_route
	
def hash_password(pwd):
	return sha1(pwd+'Yar!, Smell that s@lty see air!').hexdigest()

## Formatting

def m2j(x):
	x['id'] = x['_id']
	del x['_id']
	return json.dumps(x)

def ms2js(l):
	ls = []
	for x in l:
		x['id'] = x['_id']
		del x['_id']
		ls.append(x)
	return json.dumps(ls)

def j2m(j):
	try:
		j = json.loads(j)
	except ValueErro:
		abort(400,'Invalid JSON')
	j['_id'] = j['id']
	del j['id']
	return j
	
	
## S3

class MyStringIO(StringIO):
	def __len__(self):
		return len(self.getvalue())

			
public_acp_xml = MyStringIO(open('resources/public-acp.xml').read())
private_acp_xml = MyStringIO(open('resources/private-acp.xml').read())

	
def build_auth_sig(http_verb,path,expiration,secret_key,content_type='',content_md5='',canonical_amz_headers=''):
	to_sign = [http_verb,'\n',
				content_md5,'\n',
				content_type,'\n',
				str(int(time.mktime(expiration.timetuple()))),'\n',
				canonical_amz_headers,
				path]
	to_sign = ''.join(to_sign)
	b64sig = base64.b64encode(hmac.new(secret_key,to_sign,sha1).digest()).strip()
	return urlquote(b64sig,safe='')
	

def authed_get_url(bucket,path,expires=None):
	path = path.strip('/')
	if not expires:
		expires = datetime.datetime.now() + datetime.timedelta(0,60*10) # In 10 min
	## DEBUG:
	#expires = datetime.datetime.fromtimestamp(1141889120)
	expires_epoch_str = str(int(time.mktime(expires.timetuple())))
	sig_str = build_auth_sig('GET', path='/'+bucket+'/'+path, expiration=expires, secret_key=AWS_SECRET_ACCESS_KEY)
	
	url = ['http://s3.amazonaws.com',
			'/',bucket,'/',path,'?',
			'AWSAccessKeyId=',AWS_ACCESS_KEY_ID,'&',
			'Signature=',sig_str,'&',
			'Expires=',expires_epoch_str]
	return ''.join(url)
	
def get_stor_data(request):
	now = datetime.datetime.now()
	data = request.files.get('data')
	try:
		entity = json.loads(request.body.read())
	except ValueError:
		abort(400,"Invalid JSON")

	if entity.get('name'):
		name = entity['name']
	else:		
		name = data.filename or now.strftime("%Y-%m-%d %H:%M:%S")
	return now,name,entity

def s3put(fp,name):
	conn = S3.AWSAuthConnection(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
	response = conn.put(BUCKET_NAME,name,S3.S3Object(fp)) #,headers={'x-amz-acl':'public-read'})
	status = response.http_response.status
	if 200 > status < 300:
		abort(500, 'AWS failure: ' +response.message)
	return response


def s3del(name):
	conn = S3.AWSAuthConnection(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
	response = conn.delete(BUCKET_NAME,name) #,headers={'x-amz-acl':'public-read'})
	status = response.http_response.status
	if 200 > status < 300:
		abort(500, 'AWS failure: ' + response.message)
	return response

	
def s3setpub(name):
	conn = S3.AWSAuthConnection(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
	response = conn.put_acl(BUCKET_NAME,name,public_acp_xml)
	#s3put(public_acp_xml,name+'?acl')
	status = response.http_response.status
	print response.http_response.status
	print response.message
	if status < 200 or status > 299:
		abort(500, 'AWS failure: ' + response.message)
	return response

def s3setpriv(name):
	conn = S3.AWSAuthConnection(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
	response = conn.put_acl(BUCKET_NAME,name,private_acp_xml)
	#s3put(private_acp_xml,name+'?acl')
	status = response.http_response.status
	print response.http_response.status
	print response.message
	if status < 200 or status > 299:
		abort(500, 'AWS failure:' + response.message)
	return response

def s3name(pid,fid,entity):
	f = entity
	ext = '.'+f['ext'] if f.get('ext') else ''
	s3name = '%s-%s%s' % (pid,fid,ext)
	return s3name, ext
	
	