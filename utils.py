import json
import datetime
from bottle import request
import S3
import logging
logger = logging.getLogger()

AWS_ACCESS_KEY_ID = '0Z67F08VD9JMM1WKRDR2'
AWS_SECRET_ACCESS_KEY = 'g6o8NjU3ClIYJmaGurL+sKctlQrpEUF6irQyrpPX'
BUCKET_NAME = 'sharedocapp' # //TODO: How many buckets can I have? Maybe every pile has a bucket?


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
	response = conn.put(BUCKET_NAME,name,S3.S3Object(fp),headers={'x-amz-acl':'public-read'})

	status = response.http_response.status
	if 200 > status < 300:
		abort(400, response.message)
	return response


def s3del(name):
	conn = S3.AWSAuthConnection(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
	response = conn.delete(BUCKET_NAME,name,headers={'x-amz-acl':'public-read'})

	status = response.http_response.status
	if 200 > status < 300:
		abort(400, response.message)
	return response


def s3name(pid,fid,entity):
	f = entity
	ext = '.'+f['ext'] if f.get('ext') else ''
	s3name = '%s-%s%s' % (pid,fid,ext)
	return s3name, ext