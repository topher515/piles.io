from __future__ import with_statement
from fabric.api import local, settings, abort, run, cd, env
from fabric.contrib.console import confirm

import bottle
from bottle import template
bottle.TEMPLATES.clear()
import s3piles
import StringIO, glob
import pickle
import datetime

from settings import APP_BUCKET

from utils import app_meta

env.hosts = ['rlunch@rlunch.webfactional.com']


class MyStringIO(StringIO.StringIO):
	def __init__(self,string,*args,**kwargs):
		self._str_len = len(string)
		return StringIO.StringIO.__init__(self,string,*args,**kwargs)
	
	def __len__(self):
		return self._str_len
		

class Deployer(object):
    pass

class FileGatherer(object):
    def __init__(self):
        t = template('app',app_meta=app_meta())
        self.app_html = MyStringIO(t)
        self.app_html
        static_paths = glob.glob('static/css/*.css')
        static_paths += glob.glob('static/img/*.png')
        static_paths += glob.glob('static/img/*.gif')
        static_paths += glob.glob('static/img/*.jpg')
        static_paths += glob.glob('static/img/icons/*')
        static_paths += glob.glob('static/css/images/*.png')
        static_paths += glob.glob('static/js/*.js')
        self.static_paths = static_paths
        
        
    content_types = {
        '.js':'text/javascript',
        '.css':'text/css',
        '.html':'text/html',
        '.png':'image/png',
        '.gif':'image/gif',
        '.jpeg':'image/jpeg',
        '.jpg':'image/jpeg',
        
    }
        
    @property
    def files(self):
        yield self.app_html,'app','text/html'
        for path in self.static_paths:
            fp = open(path,'r')
            dot_index = path.rfind('.')
            ext = path[dot_index:]
            content_type = FileGatherer.content_types.get(ext)
            if not content_type:
                content_type = 'binary/octet-stream'
            yield fp,fp.name,content_type
        
        
        
        
            
class S3Deployer(Deployer):
    def __init__(self,gatherer,bucket=APP_BUCKET):
        self.bucket = bucket
        self.gatherer = gatherer
        try:
            f = open('deploy_tracker.pickle','r')
            self.change_tracker = pickle.load(f)
        except IOError:
            self.change_tracker = {}
    
    def deploy(self):  # Make sure this is public
        s3conn = s3piles.s3conn()
        print "Checking for files to upload to %s..." % self.bucket,
        count = 0
        try:
            for fp,key,content_type in self.gatherer.files:
                
                content = fp.read()
                content_hash = hash(self.bucket + content)
                if self.change_tracker.get(key) and self.change_tracker[key][0] == content_hash:
                    # print key + ' with content type ' + content_type + '...skipping.'
                    continue
            
                resp = s3conn.put(self.bucket,key,MyStringIO(content),{"x-amz-acl":"public-read",'Content-Type':content_type})
                status = resp.http_response.status
                if 200 > status < 300:
                    print "Deploy failed. Unable to upload '%s'" % fpath
                    break
                
                print key + ' with content type ' + content_type + '...uploaded.'
                count +=1
            
                self.change_tracker[key] = (content_hash,datetime.datetime.now())
            
        except:
            raise
        finally:       
            pickle.dump(self.change_tracker,open('deploy_tracker.pickle','w'))
            if count == 0:
                print "No files uploaded."
            else:
                print "...Uploaded %s files." % count
            


def wfdeploy(branch='master'):
    local("git push origin %s" % branch)
    code_dir = '~/webapps/piles_app/piles_io/'
    with cd(code_dir):
        run("git pull origin %s" % branch)
        run("../apache2/bin/restart")


def awsdeploy():
     S3Deployer(FileGatherer()).deploy()