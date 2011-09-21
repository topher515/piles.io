import json, urllib
import datetime, hashlib, random, string, os, StringIO
import bottle
import requests
from bottle import route, run, request, abort, redirect, static_file, template, response
from settings import settings
import logging
logger = logging.getLogger('piles_io.api')
from utils import *
if settings('DEPLOYED'):
    print "Importing real S3 content store."
    from contentstore import S3Store as Store
else:
    print "Importing fake content store"
    from contentstore import FakeStore as Store
from auth import hash_password, session, do_login, do_logout, auth_json

from beaker.middleware import SessionMiddleware

import usage
from db import db


### Decorators ###

class validator(object):
    def __init__(self,attrs,empty_ok=False):
        self.validators = attrs
        self.empty_ok = empty_ok
    def __call__(self,old_route):
        def new_route(*args,**kwargs):
            b =  request.body_.read()
            j = json.loads(b)
            if not j and not self.empty_ok:
                abort(400,"No JSON body found.")
            #print "got json: %s" % j
            request.validated = {}
            for valid_key,validator in self.validators.items():
                if j.get(valid_key):
                    request.validated[valid_key] = validator['type'](j[valid_key])
                elif validator.get('default',None) is not None:
                    request.validated[valid_key] = validator['default']
            #print "got validated: %s" % request.validated
            
            return old_route(*args,**kwargs)
        return new_route

def jsonp(old_route):
    def new_route(*args,**kwargs):
        if request.GET.get('callback'):
            #print response
            #print dir(response)
            response.headers['Content-Type'] = 'text/javascript; charset=UTF-8'
            wrapper = request.GET['callback']
            if request.GET.get('model'):
                body = urllib.unquote(request.GET['model'])
                request.body_ = StringIO(body)
                resp = old_route(*args,**kwargs)
                wrapper = request.GET['callback']
                return "%s(%s)" % (wrapper,resp)
            else:
                request.body_ = request.body
                return "%s(%s)" % (wrapper,old_route(*args,**kwargs) or '')
                
        else:
            request.body_ = request.body
            return old_route(*args,**kwargs)
    return new_route


class emulate_rest(object):
    def __init__(self,http_verb):
        self.http_verb = http_verb
    def __call__(self,old_route):
        http_verb = self.http_verb
        def new_route(*args,**kwargs):
            if request.method != http_verb:
                if request.method == 'POST' and request.forms.get('_method') != http_verb:
                    abort(405)
                elif request.method == 'GET' and request.GET.get('_method') != http_verb:
                    abort(405)
            return old_route(*args,**kwargs)
        return new_route


class MethodAgnosticRequestWrapper(object):
    def __init__(self,request):
        self.request = request
        
    @property
    def method(self):
        meth = self.params.get('_method','').upper()
        return meth if meth else self.request.method
        
    @property
    def params(self):
        if self.request.method == 'GET':
            return self.request.GET
        elif self.request.method == 'POST':
            return self.request.forms
        else:
            return {}
AgnosticReq = MethodAgnosticRequestWrapper
    
    

### API ###

## Feedback
@route('/feedbacks', method="ANY")
@emulate_rest('POST')
@jsonp
@validator(attrs={'message':{'type':unicode},'type':{'type':unicode},'email':{'type':unicode},'useragent':{'type':unicode}})
def feedbacks_post():
    #print request.validated
    v = request.validated
    v['datetime'] = datetime.datetime.now()
    id_ = db.feedbacks.save(v)
    v['_id'] = str(id_)
    return m2j(v)
    
    
@route('/feedbacks/:id', method="GET")
@jsonp
def feedbacks_get(id):
    feedback = db.feedbacks.find_one({'_id':id})
    return m2j(feedback) if feedback else abort(404)


### Usage
@route('/piles/:pid/usage')
@auth_json
@jsonp
def usage_summary(pid):
    um = usage.UsageMeter()
    summary = um.summary(pid)
    return m2j(summary)

@route('/piles/:pid/usage/dailies')
@auth_json
@jsonp
def usage_totals(pid):
    um = usage.UsageMeter()
    usage_dailies = um.usage_dailies(pid)
    return ms2js(usage_dailies)
    
@route('/piles/:pid/usage/monthlies')
@auth_json
@jsonp
def usage_totals(pid):
    um = usage.UsageMeter()
    usage_monthlies = um.usage_monthlies(pid)
    return ms2js(usage_monthlies)

##########################################################
## Piles
##########################################################


@route('/piles', method="GET")
@jsonp
def piles():
    if request.GET.get('email') == '!currentuser':
        s = session(request)
        if s.get('authenticated'):
            return ms2js(s['authenticated']['piles'])
    elif request.GET.get('name'):
        return ms2js(db.piles.find({'name':request.GET['name']}))


# /piles/:pid PUT
@auth_json
@jsonp
def piles_put(pid):
    
    data = request.body_.read()
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
    #   if p['_id'] == pid:
    #       s['authenticated']['piles'][i] = entity
    #       s.save()
    #print 'New auth piles: %s' % s['authenticated']['piles']
    
    do_login(request,s['authenticated']['user']) # <-- This is a pretty lame hack, but wtf? I cant figure this shit out
        
    return m2j(entity)

# /piles/:pid GET
@auth_json
@jsonp
def piles_get(pid):
    entity = db.piles.find_one({'_id':pid})
    if not entity:
        abort(404, 'No document with id %s' % id)
    return m2j(entity)


@route('/piles/:pid', method="ANY")
def piles(pid):
    areq = AgnosticReq(request)
    if areq.method == 'GET':
        return piles_get(pid)
    elif areq.method == 'PUT':
        return piles_put(pid)
    abort(405)

    
##########################################################
## Usage
##########################################################




##########################################################
## Files
##########################################################

valid_file_attrs = {
    'size':{'type':float},
    'ext':{'type':unicode},
    'id':{'type':unicode}, #fid
    'pid':{'type':unicode}, #pile id
    'pub':{'type':bool,'default':False},
    'size':{'type':int}, # bytes
    'type':{'type':unicode},
    'icon':{'type':unicode},
    'name':{'type':unicode},
    'path':{'type':unicode},  # aws s3 key
    'x':{'type':float},
    'y':{'type':float},
    'thumb':{'type':unicode},
}


# /piles/:pid/files # POST
@auth_json
@jsonp
@validator(attrs=valid_file_attrs)
def files_post(pid):
    
    
    entity = request.validated
    name = request.validated.get('name')
    fid = ''.join([random.choice(string.letters + string.digits) for x in xrange(6)]) # hashlib.md5(str(now)).hexdigest()
    #sto_file(pid,fid,name,data)
    
    valid,invalid_char = valid_chars(name)
    entity['pid'] = pid
    entity['_id'] = fid
    entity['path'] = '%s/%s/%s' % (pid,fid,name)
    if entity.get('type') in ['image/jpeg','image/gif','image/png']:
        entity['thumb'] = '%s/%s/thumb.png' % (pid,fid)
    db.files.save(entity)
    
    # Build policy and signature information 
    Store().add_storage_info(entity)
    return m2j(entity)


# /piles/:pid/files # GET
@auth_json
@jsonp
def files_get(pid):
    files = db.files.find({'pid':pid})
    return ms2js(files)


@route('/piles/:pid/files', method='ANY')
def files(pid):
    areq = AgnosticReq(request)
    if areq.method == 'POST':
        return files_post(pid)
    elif areq.method == 'GET':
        return files_get(pid)
    abort(405)



# '/piles/:pid/files/:fid', method=['PUT'
@auth_json
@jsonp
@validator(attrs=valid_file_attrs)
def file_put(pid,fid):
    
    new_entity = request.validated
    new_entity.update({'pid':pid,'name':request.validated['name'],'_id':fid})
    old_entity = db.files.find_one({'pid':pid,'_id':fid})
    
    if new_entity['pub'] and not old_entity.get('pub'):
        # This entity changed to public
        Store().setpub(new_entity['path'])
        #pass
    elif not new_entity['pub'] and old_entity.get('pub'):
        # This entity changed to private
        Store().setpriv(new_entity['path'])
        #pass
    
    # Save if the amazon change was successful
    db.files.save(new_entity)
    
    #policy,signature = build_policy_doc(new_entity['path'])
    #new_entity['policy'] = policy
    #new_entity['signature'] = signature
    return m2j(new_entity)


# '/piles/:pid/files/:fid', method=['DELETE',
@auth_json
@jsonp
def file_delete(pid,fid):
    
    entity = db.files.find_one({'pid':pid,'_id':fid})
    store = Store()
    store.delete(entity['path'])
    
    # If there's a thumbnail, delete it as well!
    if entity.get('thumb'):
        store.delete(entity['thumb'])
    
    db.files.remove(entity)
    
    # File was successfully deleted, so remove it from usage stats
    #authed = session(request)['authenticated']
    #pile = None
    #for pile in authed['piles']:
    #   if pile['_id'] == pid: break
    # Decrement storage usage 
    #print "Decrementing usage by %s" % entity['size']
    #db.piles.update({'_id':pid},{'$inc':{'usage_sto':-int(entity['size'])}})


# '/piles/:pid/files/:fid', method='GET'
@auth_json
@jsonp
def file_get(pid,fid):
    entity = db.files.find_one({'_id':fid,'pid':pid})
    if not entity:
        abort(404,"File does not exist.")
    #policy,signature = build_policy_doc(entity['path'])
    #entity['policy'] = policy
    #entity['signature'] = signature
    return m2j(entity)


@route('/piles/:pid/files/:fid', method="ANY")
def file_(pid,fid):
    areq = AgnosticReq(request)
    if areq.method == 'PUT':
        return file_put(pid,fid)
    elif areq.method == 'GET':
        return file_get(pid,fid)
    elif areq.method == 'DELETE':
        return file_delete(pid,fid)
    abort(405)
    
    
''''  <--- This is no longer necessary as users upload files directly
@route('/piles/:pid/files/:fid/content', method=['PUT','POST'])
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
    #   if pile['_id'] == pid: break
    
    #if not pile.get('usage_sto'):
    #   pile.update({'usage_sto':0,'usage_up':0,'usage_down':0})
    print "Incrementing usage by %s" % f['size']
    db.piles.update({'_id':pid},{'$inc':{'usage_sto':int(f['size']), 'usage_put':int(f['size'])}})
'''


# Public!
@route('/~:pid-:fid')
def short_file_content(pid,fid):
    f = db.files.find_one({'_id':fid,'pid':pid})
    
    um = usage.UsageMeter()
    if um.over_limit(pid):
        abort(402,"This Pile is over it's limit. The owner must pay for additional bandwidth before downloading is enabled.")
    
    uri = Store().public_get_url(f['path'])
    return redirect(uri)
    
@route('/~:pid-:fid/gregsucks')
def short_file_content_secret(pid,fid):
    ''' Secret always-enabled link
    '''
    f = db.files.find_one({'_id':fid,'pid':pid})
    uri = Store().public_get_url(f['path'])
    return redirect(uri)


@route('/piles/:pid/files/:fid/content', method='GET')
@auth_json
def get_file_content(pid,fid):
    f = db.files.find_one({'_id':fid,'pid':pid})
    
    um = usage.UsageMeter()
    if um.over_limit(pid):
        abort(402,"This Pile is over it's limit. The owner must pay for additional bandwidth before downloading is enabled.")
        
    path = f['path']
    if f['type'].startswith('image'):
        path += '?response-content-disposition=inline;%%20%s' % (f['path'])
        path += '&response-content-type=%s' % (f['type'])
    authed_url = Store().authed_get_url(path)
    return redirect(authed_url)


@route('/piles/:pid/files/:fid/thumbnail', method='GET')
@auth_json
def get_file_thumbail(pid,fid):
    f = db.files.find_one({'_id':fid,'pid':pid})
    return redirect('http://%s.s3.amazonaws.com/%s' % (BUCKET_NAME,name))