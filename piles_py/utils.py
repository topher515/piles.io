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

from settings import settings

### Utils ###

class FakeLogger(object):
    def debug(self,msg):
        print "DEBUG: %s" % msg
    def info(self,msg):
        print "INFO: %s" % msg
    def warn(self,msg):
        print "WARN: %s" % msg

class MyStringIO(StringIO):
    def __init__(self,string,*args,**kwargs):
        self._str_len = len(string)
        return StringIO.__init__(self,string,*args,**kwargs)
    
    def __len__(self):
        return self._str_len

def app_meta():
    return {
        'BUCKET_NAME':settings('APP_BUCKET'),
        'AWS_ACCESS_KEY_ID':settings('AWS_ACCESS_KEY_ID'),
        'APP_DOMAIN':settings('APP_DOMAIN'),
        'FILE_POST_URL':settings('FILE_POST_URL'),
        'APP_BUCKET_ACL':settings('APP_BUCKET_ACL'),
        'CONTENT_DOMAIN':settings('CONTENT_DOMAIN'),
    }

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
    if x.get('_id'):
        x['id'] = x['_id']
        del x['_id']
    return json.dumps(x,default=extra_json_serializers,indent=3)

def ms2js(l):
    ls = []
    for x in l:
        if x.get('_id'):
            x['id'] = x['_id']
            del x['_id']
        ls.append(x)
    return json.dumps(ls,default=extra_json_serializers)

def j2m(j):
    try:
        j = json.loads(j)
    except ValueError:
        abort(400,'Invalid JSON')
    j['_id'] = j['id']
    del j['id']
    return j
    
    
