import json
import datetime, base64, hmac, time, os
from urllib import quote as urlquote
from hashlib import sha1
from bottle import request, abort
from utils import MyStringIO
import S3
import logging
logger = logging.getLogger()

from settings import DIRNAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, APP_BUCKET, APP_BUCKET_ACL, CONTENT_DOMAIN

## S3
public_acp_xml = open(os.path.join(DIRNAME,'resources/public-acp.xml')).read()
private_acp_xml = open(os.path.join(DIRNAME,'resources/private-acp.xml')).read()


class S3Store(object):
    
    def __init__(self,s3conn=None):
        if not s3conn:
            s3conn = S3.AWSAuthConnection(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
        self.s3conn = s3conn
    
    def add_storage_info(self,entity):
        policy,signature = self.build_policy_doc(entity['path'])
        entity['policy'] = policy
        entity['signature'] = signature
        return entity
    
    def build_policy_doc(self,key):
        policy = {
            'expiration':(datetime.datetime.now()+datetime.timedelta(1)).strftime('%Y-%m-%dT%H:%M:%S.000Z'), # Valid for one day. This means the user MUST refresh the page once a day to do uploads
            'conditions': [
                {'acl':APP_BUCKET_ACL},
                {'bucket':APP_BUCKET},
                {'key': key},
                # <hack> This is a hack to allow SWF based uploads to the bucket as described here: 
                #        https://forums.aws.amazon.com/thread.jspa?messageID=77198
                # Basically flash adds a...    
                #        Content-Disposition: form-data; name="Filename"
                # ...to the end of everything it posts! 
                # Thanks Adobe! </sarcasm>
                # </hack>
            ]
        }
        policy_doc = base64.b64encode(json.dumps(policy))
        sig = base64.b64encode(hmac.new(AWS_SECRET_ACCESS_KEY,policy_doc,sha1).digest())
        return policy_doc,sig
    
    
    def build_auth_sig(self,http_verb,path,expiration,secret_key,content_type='',content_md5='',canonical_amz_headers=''):
        to_sign = [http_verb,'\n',
                    content_md5,'\n',
                    content_type,'\n',
                    str(int(time.mktime(expiration.timetuple()))),'\n',
                    canonical_amz_headers,
                    path]
        to_sign = ''.join(to_sign)
        b64sig = base64.b64encode(hmac.new(secret_key,to_sign,sha1).digest()).strip()
        return urlquote(b64sig,safe='')
    
    def public_get_url(self,path):
        return 'http://%s/%s' % (CONTENT_DOMAIN,path)

    def _authed_get_url(self,path,expires=None):
        bucket = APP_BUCKET
        path = path.strip('/')
        if not expires:
            expires = datetime.datetime.now() + datetime.timedelta(0,60*10) # In 10 min
        ## DEBUG:
        #expires = datetime.datetime.fromtimestamp(1141889120)
        expires_epoch_str = str(int(time.mktime(expires.timetuple())))
        sig_str = build_auth_sig('GET', path='/'+bucket+'/'+path, expiration=expires, secret_key=AWS_SECRET_ACCESS_KEY)
    
        url = ['http://s3.amazonaws.com',
                '/',bucket,'/',path,'?',
                'AWSAccessKeyId=',AWS_ACCESS_KEY_ID,'&',
                'Signature=',sig_str,'&',
                'Expires=',expires_epoch_str]
        return ''.join(url)

    def authed_get_url(self,path):   
        path = path.strip('/')
        #if not expires:
        #   expires = datetime.datetime.now() + datetime.timedelta(0,60*10) # In 10 min
        auth_gen = S3.QueryStringAuthGenerator(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY) #PP_BUCKET)
        #auth_gen.set_expires(expires)
        return auth_gen.get(APP_BUCKET,path)


    def put(self,fp,name):
        conn = self.s3conn
        response = conn.put(APP_BUCKET,name,S3.S3Object(fp)) #,headers={'x-amz-acl':'public-read'})
        status = response.http_response.status
        if 200 > status < 300:
            abort(500, 'AWS failure: ' +response.message)
        return response


    def delete(self,name):
        print "Deleting %s" % name
        conn = self.s3conn
        response = conn.delete(APP_BUCKET,name) #,headers={'x-amz-acl':'public-read'})
        status = response.http_response.status
        print response.http_response.status
        print response.message
        if 200 > status < 300:
            abort(500, 'AWS failure: ' + response.message)
        return response

    
    def setpub(self,name):
        conn = self.s3conn
        response = conn.put_acl(APP_BUCKET,name,MyStringIO(public_acp_xml))
        #s3put(public_acp_xml,name+'?acl')
        status = response.http_response.status
        print response.http_response.status
        print response.message
        if status < 200 or status > 299:
            abort(500, 'AWS failure: ' + response.message)
        return response

    def setpriv(self,name):
    
        conn = self.s3conn()
        response = conn.put_acl(APP_BUCKET,name,MyStringIO(private_acp_xml))
        #s3put(private_acp_xml,name+'?acl')
        status = response.http_response.status
        print response.http_response.status
        print response.message
        if status < 200 or status > 299:
            abort(500, 'AWS failure:' + response.message)
        return response
    

class FakeStore(object):
    def add_storage_info(self,entity):
        print "Pretending to append storage info."
    def public_get_url(self,name):
        print "Generating fake public get url"
        return "http://placekitten.com/200/200#Public-Kitten-URL"
    def authed_get_url(self,name):
        print "Generating fake authed get url"
        return "http://placekitten.com/300/200#Privately-Authed-URL"
    def put(self,fp,name):
        print "Pretend putting %s with name %s to content storage." % (repr(fp),name)
    def delete(self,name):
        print "Pretend deleting %s from content storage." % name
    def setpriv(self,name):
        print "Pretend setting %s to private in content storage." % name
    def setpub(self,name):
        print "Pretend setting %s to public in content storage." % name
