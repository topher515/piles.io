import json
import datetime, hashlib
import bottle
import requests
import S3
from bottle import route, run, request, abort, redirect, static_file, template
from pymongo import Connection
import logging
logger = logging.getLogger()
from PIL import Image
from tempfile import TemporaryFile as TempFile

AWS_ACCESS_KEY_ID = '0Z67F08VD9JMM1WKRDR2'
AWS_SECRET_ACCESS_KEY = 'g6o8NjU3ClIYJmaGurL+sKctlQrpEUF6irQyrpPX'
BUCKET_NAME = 'sharedocapp'


connection = Connection('localhost', 27017)
db = connection.mydatabase


### Utils ###

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


### API ###

@route('/piles/:pid', method='PUT')
def put_pile(pid):
	data = request.body.read()
	if not data:
		abort(400, 'No data received')
	try:
		entity = json.loads(data)
	except ValueError:
		abort(400, 'Invalid JSON: %s' % data)
		
	entity['_id'] = pid
	if not entity.get('emails'):
		abort(400, 'No emails associated with pile')
	if not entity.get('name'):
		abort(400, 'No name associated with pile')
		
	try:
		db.piles.save(entity)
	except ValidationError as ve:
		abort(400, str(ve))
	return m2j(entity)


@route('/piles', method='GET')
def get_piles():
	if request.GET.get('name'):
		piles = db.piles.find({'name':request.GET['name']})
	else:
		piles = db.piles.find()
		
	return ms2js(piles)
	

@route('/piles/:pid', method='GET')
def get_pile(pid):
	entity = db.piles.find_one({'_id':pid})
	if not entity:
		abort(404, 'No document with id %s' % id)
	return m2j(entity)


### Files

# Utils
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
	
# Requests
@route('/piles/:pid/files', method='POST')
def post_file(pid):
	now,name,entity = get_stor_data(request)
	fid = hashlib.md5(str(now)).hexdigest()
	#sto_file(pid,fid,name,data)
	entity['pid'] = pid
	entity['_id'] = fid
	db.files.save(entity)
	return m2j(entity)


@route('/piles/:pid/files/:fid', method='PUT')
def put_file(pid,fid):
	now,name,entity = get_stor_data(request)
	#sto_file(pid,fid,name,data)
	entity.update({'pid':pid,'name':name,'_id':fid})
	db.files.save(entity)
	return m2j(entity)


@route('/piles/:pid/files/:fid', method='DELETE')
def delete_file(pid,fid):
	entity = {'pid':pid,'_id':fid}
	s3name = '%s-%s' % (pid,fid)
	s3del(s3name)
	db.files.remove(entity)


@route('/piles/:pid/files', method='GET')
def get_files(pid):
	files = db.files.find({'pid':pid})
	return ms2js(files)


@route('/piles/:pid/files/:fid', method='GET')
def get_file(pid,fid):
	f = db.files.find_one({'_id':fid,'pid':pid})
	return m2j(f)


@route('/piles/:pid/files/:fid/content', method='PUT')
def put_file_content(pid,fid):
	f = db.files.find_one({'pid':pid,'_id':fid})
	if not f:
		abort(404,"Not a valid resource")
	data = request.files.get('files[]')
	name,ext = s3name(pid,fid,f)
	s3put(data.file,name)
	
	#thumb = TempFile() #'w+b')
	#data.file.seek(0)
	#im = Image.open(data.file)
	#im.thumbnail((128,128), Image.ANTIALIAS)
	#im.save(thumb,format=im.format)
	#s3put(thumb,name+'=s128')
	# print 'Not uploading... in test env'


@route('/piles/:pid/files/:fid/content', method='GET')
def get_file_content(pid,fid):
	f = db.files.find_one({'_id':fid,'pid':pid})
	#return json.dumps(f)
	name,ext = s3name(pid,fid,f)
	return redirect('http://%s.s3.amazonaws.com/%s' % (BUCKET_NAME,name))




@route('/piles/:pid/files/:fid/thumbnail', method='GET')
def get_file_thumbail(pid,fid):
	f = db.files.find_one({'_id':fid,'pid':pid})
	#return json.dumps(f)
	name = s3name(pid,fid,f)
	return redirect('http://%s.s3.amazonaws.com/%s' % (BUCKET_NAME,name))


### Pages ###

@route('/favicon.ico')
def favicon():
	abort(404)


@route('/static/:path#.+#')
def server_static(path):
    return static_file(path, root='static')


@route('/:pilename')
def pile(pilename):
	#r = requests.get('%s/piles?name=%s' % (API_URI,pilename))
		
	#if r.status_code != 200:
	#	return abort(r.status_code)
	#pile = json.loads(r.content)[0]
	#files = json.loads(requests.get('/piles/%(_id)s/files' % pile))
	
	pile = db.piles.find_one({'name':pilename})
	files = db.files.find({'pid':pile['_id']})
	return template('app',{'pile':m2j(pile),'files':ms2js(files)})


if __name__ == '__main__':
	bottle.debug(True)
	run(host='localhost', port=8080, reloader=True)