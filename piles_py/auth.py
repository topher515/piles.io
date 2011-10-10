import json
import datetime, base64, hmac, time, os
import itertools
from urllib import quote as urlquote
from hashlib import sha1
from bottle import request, abort
import S3
from StringIO import StringIO
import logging
logger = logging.getLogger()

from db import db


## Auth

def session(request):
	return request.environ['beaker.session']


def do_login(request,user_ent,piles=[]):
	s = session(request)
	s['authenticated'] = {'user':user_ent}
	if piles:
		s['authenticated'].update({'piles':list(piles)})
	else:
		s['authenticated'].update({'piles':list(db.piles.find({'emails':user_ent['email']}))})
	s.save()
	
	
def do_logout(request):
	s = session(request)
	s['authenticated'] = {}
	s.save()
	
	
def auth_json(old_route):
	def new_route(pid,*args,**kwargs):
		s = session(request)
		if s.get('authenticated'):
			authed = s['authenticated']
			#print "Your authed piles: %s" % authed['piles']
			authed_pids = [pile['_id'] for pile in authed['piles']]
			if pid not in authed_pids:
				abort(403,'You are not authorized to perform this action. You can only make changes to %s' % authed_pids)
			return old_route(pid,*args,**kwargs)
		else:
			abort(403,'You must be logged in to perform this action.')
	return new_route


def auth_w_redirect(old_route):
	def new_route(*args,**kwargs):
		if session(request).get('authenticated'):
			return old_route(*args,**kwargs)
		else:
			redirect('login')
	return new_route
	
	
def hash_password(pwd):
	return sha1(pwd+'Yar!, Smell that s@lty see air!').hexdigest()
