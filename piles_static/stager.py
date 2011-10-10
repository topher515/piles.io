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

    

def stage():
    '''Stage all the necessary static files!'''
    staged_dir = os.path.join(settings('DIRNAME'),'staged')
    staged_static_dir = os.path.join(staged_dir,'static')
    orig_static_dir = os.path.join(settings('DIRNAME'),'static')
    
    views_to_stage = [
        ('app',{'app_meta':app_meta()}),
        ('nodeexp',{}),
    ]
    
    # Stage the templates
    if not os.path.isdir(staged_dir):
        os.mkdir(staged_dir)
    for view,context in views_to_stage:
        html = template(v, context)
        open(os.path.join(staged_dir,view),'w').write(html)
    
    # Stage the static files!
    if not os.path.isdir(orig_static_dir):
        print "Couldn't find the static files dir"
        return
    if os.path.isdir(staged_static_dir):
        shutil.rmtree(staged_static_dir)
    shutil.copytree(orig_static_dir,staged_static_dir)
