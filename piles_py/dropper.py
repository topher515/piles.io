import json
import datetime, hashlib, random, string, os
import bottle
import requests
import uuid
from bottle import route, run, request, abort, redirect, static_file, template, post, get, response
import logging
logger = logging.getLogger('piles_io.app')

from utils import *
from api import *
from auth import hash_password, session, do_login, do_logout, auth_json, auth_w_redirect

from beaker.middleware import SessionMiddleware

from settings import settings 
bottle.TEMPLATE_PATH = settings['TEMPLATE_PATHS']

from usage import UsageMeter
from db import db, DESCENDING, ASCENDING



### Misc ###

def cors(fn):
    def wrap(*args,**kwargs):
        response.set_header('Access-Control-Allow-Origin','*')
        response.set_header('Access-Control-Allow-Method','POST, GET, OPTIONS');  
        response.set_header('Access-Control-Allow-Headers','Content-Type');
        return fn(*args,**kwargs)
    return wrap

@route('/favicon.ico')
def favicon():
    return static_file('img/pile_32.png', root='static')

valid_file_attrs = {
    'ext':{'type':unicode},
    'id':{'type':unicode}, #fid
    'pid':{'type':unicode}, #pile id
    'size':{'type':int}, # bytes
    'type':{'type':unicode},
    'icon':{'type':unicode},
    'name':{'type':unicode},
    'thumb':{'type':unicode},
}

@route('/piles/:pid/files/', method='OPTIONS')
@cors
def files_options(pid):
    pass


@get('/piles/:pid/files/')
@cors
def files_get(pid):
    files = db.files.find({'pid':pid})
    return ms2js(files)


@post('/piles/:pid/files/')
@cors
def files_post(pid):
    _entity = json.loads(request.body.read())
    entity = {}
    for attr,handler in valid_file_attrs.items():
        entity[attr] = handler['type'](_entity.get(attr))
    fid = uuid.uuid4().hex
    #valid,invalid_char = valid_chars(name)
    entity['pid'] = pid
    entity['_id'] = fid
    #entity['path'] = '%s/%s/%s' % (pid,fid,name)
    #if entity.get('type') in ['image/jpeg','image/gif','image/png']:
    #    entity['thumb'] = '%s/%s/thumb.png' % (pid,fid)
    db.files.save(entity)
    # Build policy and signature information 
    Store().add_storage_info(entity)
    return m2j(entity)

@get('/')
def root():
    redirect('http://'+settings['CONTENT_DOMAIN']+'/dropper#AABBCC')

def getapp():
    session_opts = {
        "session.type": "file",
        'session.cookie_expires': True,
        'session.auto': True,
        'session.data_dir': os.path.join(settings["DIRNAME"],"cache"),
    }
    app = bottle.default_app()
    app = SessionMiddleware(app, session_opts)
    bottle.debug(True)
    return app
    
if __name__ == '__main__':
    run(host='localhost', port=8080, app=getapp(), reloader=True)
    
