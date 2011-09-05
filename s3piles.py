import json
import datetime, base64, hmac, time, os
from urllib import quote as urlquote
from hashlib import sha1
from bottle import request, abort
import S3
from StringIO import StringIO
import logging
logger = logging.getLogger()

from settings import DIRNAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME

## S3

class MyStringIO(StringIO):
	def __len__(self):
		return len(self.getvalue())

			
public_acp_xml = MyStringIO(open(os.path.join(DIRNAME,'resources/public-acp.xml')).read())
private_acp_xml = MyStringIO(open(os.path.join(DIRNAME,'resources/private-acp.xml')).read())

	
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
	
def public_get_url(path):
	return 'http://%s.s3.amazonaws.com/%s' % (BUCKET_NAME,path)

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
	
