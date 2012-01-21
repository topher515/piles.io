from __future__ import with_statement
from fabric.api import local, abort, run, cd, env
from fabric.api import settings as fabsettings
from fabric.contrib.console import confirm

import os
#import bottle
from settings import settings
settings.require('global')
#from bottle import template
#bottle.TEMPLATES.clear()
from contentstore import S3Store
import StringIO, glob
import pickle
import datetime

from piles_static import stager

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
        """
        static_paths = glob.glob('stagedstatic/css/*.css')
        static_paths += glob.glob('static/img/*.png')
        static_paths += glob.glob('static/img/*.gif')
        static_paths += glob.glob('static/img/*.jpg')
        static_paths += glob.glob('static/img/icons/*')
        static_paths += glob.glob('static/css/images/*.png')
        static_paths += glob.glob('static/js/*.js')
        """
        
        prefix_len = len('staged/')
        self.static_paths = []
        path_search = glob.glob('staged/static/*')
        for path in path_search:
            if os.path.isdir(path):
                path_search += glob.glob(path + '/*')
            else:
                self.static_paths.append((path,path[prefix_len:]))
        
        
        
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
        # The app
        app_html = template('app',app_meta=app_meta())
        #print app_html
        yield MyStringIO(app_html),'app','text/html'
        # All other static files
        for path,name in self.static_paths:
            fp = open(path,'r')
            dot_index = path.rfind('.')
            ext = path[dot_index:]
            content_type = FileGatherer.content_types.get(ext)
            if not content_type:
                content_type = 'binary/octet-stream'
            y = fp,name,content_type
            yield y
        
        
        
            
class S3Deployer(Deployer):
    def __init__(self,gatherer,bucket=None):
        if not bucket:
            bucket = settings('APP_BUCKET')
        self.bucket = bucket
        self.gatherer = gatherer
        self.store = S3Store()
        try:
            f = open('deploy_tracker.pickle','r')
            self.change_tracker = pickle.load(f)
        except IOError:
            self.change_tracker = {}
    
    def deploy(self):  # Make sure this is public
        store = self.store
        print "Checking for files to upload to %s..." % self.bucket,
        count = 0
        try:
            for fp,key,content_type in self.gatherer.files:
                
                #print fp,key,content_type
                
                content = fp.read()
                content_hash = hash(self.bucket + content)
                if self.change_tracker.get(key) and self.change_tracker[key][0] == content_hash:
                    # print key + ' with content type ' + content_type + '...skipping.'
                    continue
            
                resp = store.put(MyStringIO(content),key,{"x-amz-acl":"public-read",'Content-Type':content_type})
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
            
            
def develop():
    local("coffee -w -c -o static/js/ static/coffee/*.coffee &")
    local("sass --watch static/css:static/css &")


def bootstrap():
    local("./piles_js/bootstrap.sh")
    local("source ./env/bin/activate")
    local("pip install -r ./piles_py/requirements.txt")


def wfdeploy(branch='master'):
    local('git add -p')
    with fabsettings(warn_only=True):
        result = local('git commit')
    local("git push origin %s" % branch)
    code_dir = '~/webapps/piles_app/piles_io/'
    with cd(code_dir):
        run("git pull origin %s" % branch)
        run("../apache2/bin/restart")


def awsdeploy():
    stager.stage()
    S3Deployer(FileGatherer()).deploy()
        