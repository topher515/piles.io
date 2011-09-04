import json
import datetime, hashlib, random, string, os
import bottle
import requests
from bottle import route, run, request, abort, redirect, static_file, template
import logging
logger = logging.getLogger('piles_io.main')
from PIL import Image
from tempfile import TemporaryFile as TempFile

from utils import *
from s3piles import *
from auth import hash_password, session, do_login, do_logout, auth_json

from beaker.middleware import SessionMiddleware

from settings import DIRNAME, TEMPLATE_PATHS # Override with local settings
bottle.TEMPLATE_PATH = TEMPLATE_PATHS

from db import db


VALID_URL_CHARS = set(string.letters + string.digits + '+_-,!')
def valid_chars(strn):
	if not strn:
		return (False,'')
	for char in strn:
		if char not in VALID_URL_CHARS:
			return (False,char)
	return (True,'')

### API ###

## Piles

@route('/piles/:pid', method='PUT')
@auth_json
def put_pile(pid):
	data = request.body.read()
	entity = json.loads(data)
		
	entity['_id'] = pid
	if not entity.get('emails'):
		abort(400, 'No emails associated with pile')
	if not entity.get('name'):
		abort(400, 'No name associated with pile')
		
	valid,badness = valid_chars(entity['name'])
	if not valid:
		abort(400, 'Not a valid name')
		
	try:
		db.piles.save(entity)
	except ValidationError as ve:
		abort(400, str(ve))
	return m2j(entity)


@route('/piles', method='GET')
@auth_json
def get_piles():
	if request.GET.get('name'):
		piles = db.piles.find({'name':request.GET['name']})
	else:
		piles = db.piles.find()
		
	return ms2js(piles)
	

@route('/piles/:pid', method='GET')
@auth_json
def get_pile(pid):
	entity = db.piles.find_one({'_id':pid})
	if not entity:
		abort(404, 'No document with id %s' % id)
	return m2j(entity)

## Files

@route('/piles/:pid/files', method='POST')
@auth_json
def post_file(pid):
	now,name,entity = get_stor_data(request)
	fid = ''.join([random.choice(string.letters + string.digits) for x in xrange(6)]) # hashlib.md5(str(now)).hexdigest()
	#sto_file(pid,fid,name,data)
	
	valid,invalid_char = valid_chars(name)
	entity['pid'] = pid
	entity['_id'] = fid
	entity['path'] = '%s-%s-%s' % (pid,fid,name)
	db.files.save(entity)
	return m2j(entity)


@route('/piles/:pid/files/:fid', method='PUT')
@auth_json
def put_file(pid,fid):
	now,name,new_entity = get_stor_data(request)
	new_entity.update({'pid':pid,'name':name,'_id':fid})
	old_entity = db.files.find_one({'pid':pid,'_id':fid})
	
	if new_entity['pub'] and not old_entity.get('pub'):
		# This entity changed to public
		s3setpub(new_entity['path'])
		#pass
	elif not new_entity['pub'] and old_entity.get('pub'):
		# This entity changed to private
		s3setpriv(new_entity['path'])
		#pass
	
	# Save if the amazon change was successful
	db.files.save(new_entity)
	
	return m2j(new_entity)


@route('/piles/:pid/files/:fid', method='DELETE')
@auth_json
def delete_file(pid,fid):
	entity = db.files.find_one({'pid':pid,'_id':fid})
	s3del(entity['path'])
	db.files.remove(entity)


@route('/piles/:pid/files', method='GET')
@auth_json
def get_files(pid):
	files = db.files.find({'pid':pid})
	return ms2js(files)


@route('/piles/:pid/files/:fid', method='GET')
@auth_json
def get_file(pid,fid):
	f = db.files.find_one({'_id':fid,'pid':pid})
	return m2j(f)


@route('/piles/:pid/files/:fid/content', method='PUT')
@auth_json
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

# Public!
@route('/~:pid-:fid')
def short_file_content(pid,fid):
	f = db.files.find_one({'_id':fid,'pid':pid})
	return redirect(public_get_url(f['path']))

@route('/piles/:pid/files/:fid/content', method='GET')
@auth_json
def get_file_content(pid,fid):
	f = db.files.find_one({'_id':fid,'pid':pid})
	#return json.dumps(f)
	#name,ext = s3name(pid,fid,f)
	authed_url = authed_get_url(BUCKET_NAME,f['path'])
	#print authed_url
	return redirect(authed_url)


@route('/piles/:pid/files/:fid/thumbnail', method='GET')
@auth_json
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
	user_ent = s.get('authenticated')
	print user_ent
	if not user_ent:
		return redirect('/login')
	pile = db.piles.find_one({'emails':user_ent.get('email')})
	if not pile:
		return abort(404,'Your user account does not have a Pile associated with it. Please report this error!')
	return redirect('/'+pile['name'])

@route('/create', method="GET")
def create():
	return template('create',name="Name for your pile",email='Email',password="Password",code='Invite Code',errors=[])

@route('/create', method="POST")
def create_do():
	eml = request.forms.get('email')
	pwd = request.forms.get('password')
	code = request.forms.get('code')
	name = request.forms.get('name')
	kwargs = {"email":eml,"password":pwd,"code":code,"name":name,"errors":[]}
	if not eml or '@' not in eml or not pwd:
		kwargs['errors'].append("Please enter a valid username and password")
		return template('create',**kwargs)
	
	user = db.users.find_one({'email':eml})
	print user
	if user:
		kwargs['errors'].append('That email is already in use! Maybe you want to <a class="btn small" href="/login">login</a>?')
		return template('create',**kwargs)
	
	if not name or name.lower() == 'name':
		stupid = ['Jills_Mortuary--You_kill_Em_We_Chill_Em','no_fatties,please','Hey!','wonderful-bill','DataDyne-Inc.',\
			'Wonderful_Me','programmers-delight','The_Colbert_Nation','WackoMan','the-ugly-duckling']
		kwargs['errors'].append("You must provide a name for your pile. Like '%s' or '%s'" % (random.choice(stupid),random.choice(stupid)))
		return template('create',**kwargs)
	
	valid,invalid_char = valid_chars(name)
	if not valid:
		kwargs['errors'].append("That is an invalid name. Just use letters, numbers and '_-,+'. You can't use '%s'." % invalid_char)
		return template('create',**kwargs)
	
	if db.piles.find_one({'name':name}):
		kwargs['errors'].append('Sorry, that pile name is already in use!')
		return template('create',**kwargs)
	
	invite = db.invites.find_one({'code':code})
	if not invite:
		kwargs['errors'].append("That is an invalid code or has already been used. Sorry.")
		return template('create',**kwargs)
	
	if invite.get('remaining', 1) == 1:
		db.invites.remove(invite)
	else:
		invite['remaining'] -= 1
		db.invites.save(invite)
	
	randid = lambda: ''.join([random.choice(string.letters + string.digits) for x in xrange(6)])
	pid = randid()
	while db.piles.find_one({"_id":pid}):
		pid = randid()
	
	user = {'email':eml,'password':hash_password(pwd)}
	pile = {'_id':pid,'emails':[eml],'name':name,'welcome':True}
	db.piles.save(pile)
	db.users.save(user)
	
	do_login(request,user) # Let the login look up the piles because they might have more than one!
	
	return redirect('/%s' % pile['name'])


@route('/login', method="GET")
def login():
	return template('login',email='Email',errors=[])

@route('/login', method="POST")
def login_do():
	if not request.forms.get('email') or not request.forms.get('password'):
		return template('login',email=request.forms['email'],errors=['No username or password'])
		
	hashed_pwd = hash_password(request.forms['password'])
	email = request.forms['email'].lower()
	user_ent = db.users.find_one({"email":email,"password":hashed_pwd})
	if not user_ent:
		return template('login',email=request.forms['email'],errors=['Bad email or password'])
		
	piles = list(db.piles.find({'emails':email}))
	
	do_login(request,user_ent,piles)
	
	print piles
	if piles:
		return redirect('/'+piles[0]['name'])
	else:
		return redirect('/broke')

@route('/logout')
def logout():
	do_logout(request)
	print "Logged out..."
	redirect('/login')
	

@route('/:pilename')
def pile(pilename):
	
	pile = db.piles.find_one({'name':pilename})
	if not pile:
		abort(404,'That Pile does not exist.')
	
	s = session(request)
	if s.get('authenticated'):
		if pile['_id'] in [ p['_id'] for p in s['authenticated']['piles'] ]:
			files = db.files.find({'pid':pile['_id']})
			return template('app',{'pile':m2j(pile),'files':ms2js(files)})
	
	files = db.files.find({'pid':pile['_id'],'pub':True})
	return template('app_public',pile=pile,files=list(files))


def getapp():
	session_opts = {
		"session.type": "file",
		'session.cookie_expires': True,
		'session.auto': True,
		'session.data_dir': os.path.join(DIRNAME,"cache"),
	}
	app = bottle.default_app()
	app = SessionMiddleware(app, session_opts)
	bottle.debug(True)
	return app
	
if __name__ == '__main__':
	run(host='localhost', port=8080, app=getapp(), reloader=True)
	