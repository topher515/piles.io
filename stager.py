import os
import bottle
from bottle import route, run, request, abort, redirect, static_file, template
import shutil
import logging
logger = logging.getLogger('piles_io.api')
from StringIO import StringIO
from PIL import Image
from base64 import b64encode, b64decode

from utils import app_meta

from settings import settings # Override with local settings
bottle.TEMPLATE_PATH = settings('TEMPLATE_PATHS')



### Static Files ###

@route('/', method='POST')
def file_post():
    print "Simulated file post"
    print request.forms.items()
    print "Reading file with name %s..." % request.files['file'].filename,
    try:
        fileread = request.files['file'].file.read()
        print "Read file successfully"
    except:
        print "Failed to read file!"
        
    try:
        im = Image.open(StringIO(fileread))
        print "Got image: %s" % im
    except:
        from traceback import print_exc
        print_exc()
        #print "================================================"
        #print fileread #b64encode(fileread)
        #print "================================================"
        
    print "...done reading."
    

@route('/:path#.+#')
def server_static(path):
    '''Serve the staged static files'''
    return static_file(path, root='staged')

def stage():
    '''Stage all the necessary static files!'''
    staged_dir = os.path.join(settings('DIRNAME'),'staged')
    staged_static_dir = os.path.join(staged_dir,'static')
    orig_static_dir = os.path.join(settings('DIRNAME'),'static')
    
    # Stage the app
    if not os.path.isdir(staged_dir):
        os.mkdir(staged_dir)
    app_html = template('app', app_meta=app_meta())
    open(os.path.join(staged_dir,'app'),'w').write(app_html)
    
    # Stage the static files!
    if not os.path.isdir(orig_static_dir):
        print "Couldn't find the static files dir"
        return
    if os.path.isdir(staged_static_dir):
        shutil.rmtree(staged_static_dir)
    shutil.copytree(orig_static_dir,staged_static_dir)


if __name__ == '__main__':    
    app = bottle.default_app()
    stage()
    run(host='localhost', port=9090, app=app, reloader=True)