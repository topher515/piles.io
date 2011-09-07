import json
import datetime, hashlib, random, string, os
import bottle
import requests
from bottle import route, run, request, abort, redirect, static_file, template
import logging
logger = logging.getLogger('piles_io.main')
from utils import *
from s3piles import *
from auth import hash_password, session, do_login, do_logout, auth_json

from beaker.middleware import SessionMiddleware


from db import db


class validator(object):
	def __init__(self,types,empty_ok=False):
		self.validators = types
		self.empty_ok = empty_ok
	def __call__(self,old_route):
		def new_route(*args,**kwargs):
			j = json.loads(request.body.read())
			if not j and not self.empty_ok:
				abort(400,"No JSON body found.")
			#print "got json: %s" % j
			request.validated = {}
			for valid_key,validator in self.validators.items():
				if j.get(valid_key):
					request.validated[valid_key] = validator(j[valid_key])
			#print "got validated: %s" % request.validated
			return old_route(*args,**kwargs)
		return new_route


### API ###

## Feedback

@route('/feedbacks', method="POST")
@validator(types={'message':unicode,'type':unicode,'email':unicode},)
def feedback_post():
	#print request.validated
	v = request.validated
	v['datetime'] = datetime.datetime.now()
	id_ = db.feedbacks.save(v)
	v['_id'] = str(id_)
	return m2j(v)
	
	
@route('/feedbacks/:id', method="GET")
def feedback_get(id):
	feedback = db.feedbacks.find_one({'_id':id})
	return m2j(feedback) if feedback else abort(404)


## Piles

@route('/piles/:pid', method='PUT')
@auth_json
def put_pile(pid):
	data = request.body.read()
	entity = j2m(data)

	if not entity.get('emails'):
		abort(400, 'No emails associated with pile')
	if not entity.get('name'):
		abort(400, 'No name associated with pile')
		
	valid,badness = valid_chars(entity['name'])
	if not valid:
		abort(400, "Not a valid name. You can't use the characters %s" % badness)
		
	try:
		db.piles.save(entity)
	except ValidationError as ve:
		abort(400, str(ve))
		
	#print "The new pile entity being saved: %s" % entity
	s = session(request)
	#for i,p in enumerate(s['authenticated']['piles']):
	#	if p['_id'] == pid:
	#		s['authenticated']['piles'][i] = entity
	#		s.save()
	#print 'New auth piles: %s' % s['authenticated']['piles']
	
	do_login(request,s['authenticated']['user']) # <-- This is a pretty lame hack, but wtf? I cant figure this shit out
		
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
	
	# File was successfully deleted, so remove it from usage stats
	#authed = session(request)['authenticated']
	#pile = None
	#for pile in authed['piles']:
	#	if pile['_id'] == pid: break
	# Decrement storage usage 
	print "Decrementing usage by %s" % entity['size']
	db.piles.update({'_id':pid},{'$inc':{'usage_sto':-int(entity['size'])}})


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
	s3put(data.file,f['path'])
	
	# The file has successfully uploaded so let's add this to their usage
	#authed = session(request)['authenticated']
	#pile = None
	#for pile in authed['piles']:
	#	if pile['_id'] == pid: break
	
	#if not pile.get('usage_sto'):
	#	pile.update({'usage_sto':0,'usage_up':0,'usage_down':0})
	print "Incrementing usage by %s" % f['size']
	db.piles.update({'_id':pid},{'$inc':{'usage_sto':int(f['size']), 'usage_put':int(f['size'])}})

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
	authed_url = authed_get_url(f['path'])
	#print authed_url
	return redirect(authed_url)


@route('/piles/:pid/files/:fid/thumbnail', method='GET')
@auth_json
def get_file_thumbail(pid,fid):
	f = db.files.find_one({'_id':fid,'pid':pid})
	#return json.dumps(f)
	# name = s3name(pid,fid,f)
	return redirect('http://%s.s3.amazonaws.com/%s' % (BUCKET_NAME,name))