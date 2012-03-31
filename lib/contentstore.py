import json
import datetime, base64, hmac, time, os
from urllib import quote as urlquote
from hashlib import sha1
from bottle import request, abort
from utils import MyStringIO
import S3
import logging
logger = logging.getLogger()

public_acp_xml_tpl = """<?xml version="1.0" encoding="UTF-8"?><AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Owner><ID>{%(id)s}</ID><DisplayName>{%(display_name)s}</DisplayName></Owner><AccessControlList><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser"><ID>{%(id)s}</ID><DisplayName>{%(display_name)s}</DisplayName></Grantee><Permission>READ</Permission></Grant><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser"><ID>{%(id)s}</ID><DisplayName>{%(display_name)s}</DisplayName></Grantee><Permission>WRITE</Permission></Grant><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser"><ID>{%(id)s}</ID><DisplayName>{%(display_name)s}</DisplayName></Grantee><Permission>READ_ACP</Permission></Grant><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser"><ID>{%(id)s}</ID><DisplayName>{%(display_name)s}</DisplayName></Grantee><Permission>WRITE_ACP</Permission></Grant><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="Group"><URI>http://acs.amazonaws.com/groups/global/AllUsers</URI></Grantee><Permission>READ</Permission></Grant></AccessControlList></AccessControlPolicy>"""
private_acp_xml_tpl = """<?xml version="1.0" encoding="UTF-8"?><AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Owner><ID>{%(id)s}</ID><DisplayName>{%(display_name)s}</DisplayName></Owner><AccessControlList><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser"><ID>{%(id)s}</ID><DisplayName>{%(display_name)s}</DisplayName></Grantee><Permission>READ</Permission></Grant><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser"><ID>{%(id)s}</ID><DisplayName>{%(display_name)s}</DisplayName></Grantee><Permission>WRITE</Permission></Grant><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser"><ID>{%(id)s}</ID><DisplayName>{%(display_name)s}</DisplayName></Grantee><Permission>READ_ACP</Permission></Grant><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser"><ID>{%(id)s}</ID><DisplayName>{%(display_name)s}</DisplayName></Grantee><Permission>WRITE_ACP</Permission></Grant></AccessControlList></AccessControlPolicy>"""


class UnspecifiedCanonicalUserId(Exception):
    pass

class S3Store(object):
    
    def __init__(self,s3conn,bucket,canonical_user={},bucket_acl='private'):
        self.canonical_user = canonical_user
        if isinstance(s3conn,S3.AWSAuthConnection):
            self.s3conn = s3conn
        else:
            self.s3conn = S3.AWSAuthConnection(s3conn[0],s3conn[1])
        self.bucket = bucket
    
    def _get_public_acp_xml(self):
        if not self.canonical_user:
            raise UnspecifiedCanoncialUser
    
    def _get_private_acp_xml(self):
        if not self.canonical_user:
            raise UnspecifiedCanoncialUser
        
        
    
    public_acp_xml = property(_get_public_acp_xml)
    private_acp_xml = property(_get_private_acp_xml)
    
    aws_secret_access_key = property(lambda s: s.s3conn.aws_secret_access_key)
    aws_access_key_id = property(lambda s: s.s3conn.aws_access_key_id)
    
    def add_storage_info(self,entity):
        
        disp = 'inline;' if entity['type'].startswith('image') else 'attachment;'
        
        policy,signature = self.build_policy_doc(entity['path'], content_type=entity['type'], content_disposition=disp )
        entity['policy'] = policy
        entity['signature'] = signature
        
        if entity.get('thumb'):
            policy,signature = self.build_policy_doc(entity['thumb'], content_type='image/png', content_disposition='inline; ', acl='public-read')
            entity['thumb_policy'] = policy
            entity['thumb_signature'] = signature
        return entity
    
    def build_policy_doc(self,key,content_type,content_disposition,acl=''):
        if not acl:
            acl = self.bucket_acl
        
        policy = {
            'expiration':(datetime.datetime.now()+datetime.timedelta(1)).strftime('%Y-%m-%dT%H:%M:%S.000Z'), # Valid for one day. This means the user MUST refresh the page once a day to do uploads
            'conditions': [
                {'acl':acl},
                {'bucket':self.bucket},
                {'key': key}, # Key must match our key *Exactly*
                ["starts-with", "$Content-Type", ""], # Content-type can be anything
                ["starts-with", "$Content-Disposition", ""], # Content-disposition can be anything
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
        sig = base64.b64encode(hmac.new(self.aws_secret_access_key,policy_doc,sha1).digest())
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
        

    def _authed_get_url(self,path,expires=None):
        bucket = self.bucket
        path = path.strip('/')
        if not expires:
            expires = datetime.datetime.now() + datetime.timedelta(0,60*10) # In 10 min
        ## DEBUG:
        #expires = datetime.datetime.fromtimestamp(1141889120)
        expires_epoch_str = str(int(time.mktime(expires.timetuple())))
        sig_str = build_auth_sig('GET', path='/'+bucket+'/'+path, expiration=expires, secret_key=self.aws_secret_access_key)
    
        url = ['http://s3.amazonaws.com',
                '/',bucket,'/',path,'?',
                'AWSAccessKeyId=',AWS_ACCESS_KEY_ID,'&',
                'Signature=',sig_str,'&',
                'Expires=',expires_epoch_str]
        return ''.join(url)

    def authed_get_url(self,path):   
        path = path.strip('/') # Normalize path by dropping extra begin/end slashes

        auth_gen = S3.QueryStringAuthGenerator(self.aws_access_key_id,self.aws_secret_access_key, is_secure=False) #PP_BUCKET)
        
        # if not expires:
        #    expires = datetime.datetime.now() + datetime.timedelta(0,60*10) # In 10 min
        # auth_gen.set_expires(expires)
        
        uri = auth_gen.get(self.bucket,path)
        
        # We actually want to `unquote` the `/` char to allow for prettier key URLs
        #i = uri.index('?')
        #lside = uri[:i].replace('%2F','/')
        #rside = uri[i:]
        return uri


    def put(self,fp,name,options={}):
        conn = self.s3conn
        response = conn.put(self.bucket,name,S3.S3Object(fp),options) #,headers={'x-amz-acl':'public-read'})
        status = response.http_response.status
        if 200 > status < 300:
            abort(500, 'AWS failure: ' +response.message)
        return response


    def delete(self,name):
        print "Deleting %s" % name
        conn = self.s3conn
        response = conn.delete(self.bucket,name) #,headers={'x-amz-acl':'public-read'})
        status = response.http_response.status
        print response.http_response.status
        print response.message
        if 200 > status < 300:
            abort(500, 'AWS failure: ' + response.message)
        return response

    
    def setpub(self,name):
        if not self.canonical_user_id:
            raise UnspecifiedCanoncialUserId
        conn = self.s3conn
        response = conn.put_acl(self.bucket,name,MyStringIO(self.public_acp_xml))
        #s3put(public_acp_xml,name+'?acl')
        status = response.http_response.status
        print response.http_response.status
        print response.message
        if status < 200 or status > 299:
            abort(500, 'AWS failure: ' + response.message)
        return response

    def setpriv(self,name):
        conn = self.s3conn
        response = conn.put_acl(self.bucket,name,MyStringIO(self.private_acp_xml))
        #s3put(private_acp_xml,name+'?acl')
        status = response.http_response.status
        print response.http_response.status
        print response.message
        if status < 200 or status > 299:
            abort(500, 'AWS failure:' + response.message)
        return response
    
    def list_bucket(self,*args,**kwargs):
        return self.s3conn.list_bucket(self.bucket,*args,**kwargs)
        
    def get(self,*args,**kwargs):
        return self.s3conn.get(self.bucket,*args,**kwargs)
    

class FakeStore(object):
    def add_storage_info(self,entity):
        policy,signature = ('kittens_are_great','John Hancock')
        entity['policy'] = policy
        entity['signature'] = signature
        if entity.get('thumb'):
            policy,signature = ('kittens_are_great_thumbnail','John Hancock_thumbnail')
            entity['thumb_policy'] = policy
            entity['thumb_signature'] = signature
        print "Pretending to append storage info."
    def public_get_url(self,name):
        print "Generating fake public get url"
        return "http://placekitten.com/200/200?Public-Kitten-URL=true"
    def authed_get_url(self,name):
        print "Generating fake authed get url"
        return "http://placekitten.com/300/200?Privately-Authed-URL=true"
    def put(self,fp,name):
        print "Pretend putting %s with name %s to content storage." % (repr(fp),name)
    def delete(self,name):
        print "Pretend deleting %s from content storage." % name
    def setpriv(self,name):
        print "Pretend setting %s to private in content storage." % name
    def setpub(self,name):
        print "Pretend setting %s to public in content storage." % name
