import json
import datetime, base64, hmac, time, os
from urllib import quote as urlquote
from hashlib import sha1
from bottle import request, abort
import S3
from StringIO import StringIO
import logging
logger = logging.getLogger()


### Utils ###
## Formatting

def human_size(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

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
	
	
