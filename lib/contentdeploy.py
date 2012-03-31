from __future__ import with_statement

import os
from contentstore import S3Store
import StringIO, glob
import pickle
import datetime


class StringIOHack(StringIO.StringIO):
	def __init__(self,string,*args,**kwargs):
		self._str_len = len(string)
		return StringIO.StringIO.__init__(self,string,*args,**kwargs)

	def __len__(self):
		return self._str_len


class FileGatherer(object):
    def __init__(self,root_path):        
        prefix_len = len(root_path + '/')
        self.static_paths = []
        path_search = glob.glob(root_path + '/*')
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
        

class ContentDeployer(object):
    pass

class S3Deployer(ContentDeployer):
    def __init__(self,gather,bucket):
        self.bucket = bucket
        if isinstance(gather,isinstace(FileGatherer)):
            self.gatherer = gather
        else:
            self.gatherer = FileGatherer(gather)
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
            
                resp = store.put(StringIOHack(content),key,{"x-amz-acl":"public-read",'Content-Type':content_type})
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