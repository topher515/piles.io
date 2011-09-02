import json
import datetime, hashlib, random, string
import bottle
import requests
from bottle import route, run, request, abort, redirect, static_file, template
from pymongo import Connection
import logging
logger = logging.getLogger()
from PIL import Image
from tempfile import TemporaryFile as TempFile
from utils import *

from beaker.middleware import SessionMiddleware

connection = Connection('localhost', 27017)
db = connection.mydatabase


### API ###

## Piles

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

## Files

@route('/piles/:pid/files', method='POST')
def post_file(pid):
	now,name,entity = get_stor_data(request)
	fid = ''.join([random.choice(string.letters + string.digits) for x in xrange(6)]) # hashlib.md5(str(now)).hexdigest()
	#sto_file(pid,fid,name,data)
	entity['pid'] = pid
	entity['_id'] = fid
	entity['path'] = '%s-%s-%s' % (pid,fid,name)
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
	entity = db.files.find_one({'pid':pid,'_id':fid})
	s3del(entity['path'])
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
	#name,ext = s3name(pid,fid,f)
	s3put(data.file,f['path'])
	
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
	#name,ext = s3name(pid,fid,f)
	authed_url = authed_get_url(BUCKET_NAME,f['path'])
	#print authed_url
	return redirect(authed_url)


@route('/piles/:pid/files/:fid/thumbnail', method='GET')
def get_file_thumbail(pid,fid):
	f = db.files.find_one({'_id':fid,'pid':pid})
	#return json.dumps(f)
	# name = s3name(pid,fid,f)
	return redirect('http://%s.s3.amazonaws.com/%s' % (BUCKET_NAME,name))




### Misc ###

@route('/favicon.ico')
def favicon():
	abort(404)

### Static Files ###

@route('/static/:path#.+#')
def server_static(path):
    return static_file(path, root='static')


### Pages ###

@route('/')
def front():
	s = session(request)
	user_ent =s['authenticated_as']
	pile = db.piles.find_one({'emails':user_ent['email']})
	return redirect('/'+pile['name'])

@route('/create')
def create():
	return "Not implemented yet"

@route('/login', method="GET")
def login():
	return template('login',email='',errors=[])

@route('/login', method="POST")
def login():
	if not request.forms.get('email') or not request.forms.get('password'):
		return template('login',email=request.forms['email'],errors=['No username or password'])
		
	hashed_pwd = hashlib.sha1(request.forms['password']).hexdigest()
	email = request.forms['email'].lower()
	user_ent = db.users.find_one({"email":email,"password":hashed_pwd})
	if not user_ent:
		return template('login',email=request.forms['email'],errors=['Bad email or password'])
		
	s = session(request)
	s['authenticated_as'] = user_ent
	s.save()
	pile = db.piles.find_one({'emails':email})
	print pile
	if pile:
		return redirect('/'+pile['name'])
	else:
		return redirect('/create')

@route('/logout')
def logout():
	s = session(request)
	s['authenticated_as'] = None
	s.save()
	print "Logged out..."
	redirect('/login')
	

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
	session_opts = {
		"session.type": "file",
		'session.cookie_expires': True,
		'session.auto': True,
		'session.data_dir': "cache",
	}
	app = bottle.default_app()
	app = SessionMiddleware(app, session_opts)
	bottle.debug(True)
	run(host='localhost', port=8080, app=app, reloader=True)