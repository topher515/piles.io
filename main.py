import json
import datetime, hashlib, random, string, os
import bottle
import requests
from bottle import route, run, request, abort, redirect, static_file, template
import logging
logger = logging.getLogger('piles_io.api')

from utils import *
from s3piles import *
from api import *
from auth import hash_password, session, do_login, do_logout, auth_json, auth_w_redirect

from beaker.middleware import SessionMiddleware

from settings import DIRNAME, TEMPLATE_PATHS # Override with local settings
bottle.TEMPLATE_PATH = TEMPLATE_PATHS

from db import db





### Misc ###

@route('/favicon.ico')
def favicon():
	return static_file('img/pile_32.png', root='static')

### Static Files ###

@route('/static/:path#.+#')
def server_static(path):
    return static_file(path, root='static')


### Pages ###

@route('/')
def front():
	s = session(request)
	authed = s.get('authenticated')
	if not authed:
		return redirect('/login')
	pile = authed['piles'][0]
	if not pile:
		return abort(404,'Your user account (%s) does not have a Pile associated with it. Please report this error!' % user_ent['email'])
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
	pile = {'_id':pid,'emails':[eml],'name':name,'welcome':True,'usage_put':0,'usage_get':0,'usage_sto':0}
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
	
	
@route('/verify',method="GET")
def verify():
	code = request.GET.get('code')
	email = request.GET.get('email')
	if not code or not email:
		return template('verify',code='Verification Code',email='Email',errors=['Enter a valid code and email address'])
	
	verify = db.verifies.find_one({'code':code,'email':email})
	if verify:
		s = session(request)
		if not s.get('messages'):
			s['messages'] = []
		s['messages'].append('Email verified.')
		return redirect('/')
	else:
		return template('verify',code=code,email=email,errors=['Enter a valid code and email address'])


@route('/password',method="GET")
def password():
	share = db.shares.find_one({'code':code})
	if not share:
		abort(400,"That's not a valid code.")
	return template('password', code=request.GET.get('code'))
	
	
@route('/password', method='POST')
def password_do():
	code = request.forms.get('code')
	share = db.shares.find_one({'code':code})
	if not share:
		abort(400,"That is not a valid password reset code.")
	user = db.users.find_one({'email':share['email']})
	user['password'] = hash_password(request.forms.get('new_password'))
	db.users.save(user)
	do_login(request,user)
	return redirect('/')


@route('/:pilename/usage', method="GET")
@auth_w_redirect
def usage(pilename):
	pile = db.piles.find_one({'name':pilename})
	if not pile:
		abort(404,'That Pile does not exist.')
		
	s = session(request)
	if s.get('authenticated') and not request.GET.get('public'):
		authed_piles = [ p['_id'] for p in s['authenticated']['piles'] ]
		if pile['_id'] in authed_piles:
			files = db.files.find({'pid':pile['_id']})
			return template('usage',{'pile':pile,'files':files})
		
	return redirect('/'+pilename)
	

@route('/s3test/:key')
def s3test(key):
    policy,signature = build_policy_doc(key)
    return template('s3test',key=key,policy=policy,signature=signature)

@route('/app')
def app():
    return template('app',app_meta=app_meta())


@route('/:pilename')
def pile(pilename):
	
	pile = db.piles.find_one({'name':pilename})
	if not pile:
		abort(404,'That Pile does not exist.')
	
	s = session(request)
	if s.get('authenticated') and not request.GET.get('public'):
		authed_piles = [ p['_id'] for p in s['authenticated']['piles'] ]
		if pile['_id'] in authed_piles:
			files = db.files.find({'pid':pile['_id']})
			return template('app',{'pile':pile,'files':files,'app_meta':app_meta()})
	
	files = db.files.find({'pid':pile['_id'],'pub':True})
	return template('app_public',pile=pile,files=list(files),authenticated=s.get('authenticated',{}))


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
	