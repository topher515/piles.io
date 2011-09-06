import json
import datetime, base64, hmac, time, os, string
from urllib import quote as urlquote
from hashlib import sha1
from bottle import request, abort
import S3
from StringIO import StringIO
import logging
logger = logging.getLogger()
from smtplib import SMTP

from settings import EMAIL_BOX_NAME, EMAIL_BOX_PWD, EMAIL_FROM_ADDR, EMAIL_SMTP_HOST

### Utils ###

def extra_json_serializers(python_object):                                             
	if isinstance(python_object, datetime.datetime):                                
		return str(python_object)
	raise TypeError(repr(python_object) + ' is not JSON serializable')


VALID_URL_CHARS = set(string.letters + string.digits + '+_-,!')
def valid_chars(strn):
	if not strn:
		return (False,'')
	for char in strn:
		if char not in VALID_URL_CHARS:
			return (False,char)
	return (True,'')

## Email
def send_email(to_addrs,msg):
	#from_addr = 'my_email_address@mydomain.tld'
	#to_addrs = ['team@mydomain.tld']
	#msg = open('email_msg.txt','r').read()
	s = SMTP()
	s.connect(EMAIL_SMTP_HOST)
	s.login(EMAIL_BOX_NAME,EMAIL_BOX_PWD)
	s.sendmail(EMAIL_FROM_ADDR, to_addrs, msg)

## Formatting
def human_size(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

def m2j(x):
	x['id'] = x['_id']
	del x['_id']
	return json.dumps(x,default=extra_json_serializers)

def ms2js(l):
	ls = []
	for x in l:
		x['id'] = x['_id']
		del x['_id']
		ls.append(x)
	return json.dumps(ls,default=extra_json_serializers)

def j2m(j):
	try:
		j = json.loads(j)
	except ValueErro:
		abort(400,'Invalid JSON')
	j['_id'] = j['id']
	del j['id']
	return j
	
	
