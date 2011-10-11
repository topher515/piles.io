import os, yaml
import bottle
from bottle import template
# from bottle_pystache import template
import shutil
import logging
logger = logging.getLogger('piles_static.stager')
from utils import get_app_context

settings = yaml.load(open('settings.yml','r'))

bottle.TEMPLATE_PATH = [os.path.join(settings['DIRNAME'],'templates')]

    


def stage():
    '''Stage all the necessary static files!'''
    staged_dir = os.path.join(settings['DIRNAME'],'staged')
    staged_static_dir = os.path.join(staged_dir,'static')
    orig_static_dir = os.path.join(settings['DIRNAME'],'static')
    
    views_to_stage = [
        ('app',get_app_context()),
        ('nodeexp',{}),
    ]
    
    # Stage the templates
    if not os.path.isdir(staged_dir):
        os.mkdir(staged_dir)
    for view,context in views_to_stage:
        html = template(view, context)
        open(os.path.join(staged_dir,view),'w').write(html)
    
    # Stage the static files!
    if not os.path.isdir(orig_static_dir):
        print "Couldn't find the static files dir"
        return
    if os.path.isdir(staged_static_dir):
        shutil.rmtree(staged_static_dir)
    shutil.copytree(orig_static_dir,staged_static_dir)

if __name__ == '__main__':
    stage()