from __future__ import print_function

from fabric.api import local #, abort, run, cd, env
#from fabric.api import settings as fabsettings
#from fabric.contrib.console import confirm

import os, yaml
import glob
from pystache import loader, view
import shutil
    
from piles_static import serve as static_serve

from settings import env
settings = env('development')

staged_dir = os.path.join(settings['DIRNAME'],'staged')
orig_static_dir = os.path.join(settings['DIRNAME'],'static')
    
def renderer(viewname,context):
    ctx = dict(context)
    view.View.template_path = settings['DIRNAME']+'/views'
    
    v = view.View(context=ctx)
    v.template_name = viewname
    inner = v.render()
    # Add to context 
    ctx.update({'body':inner,'yield':inner})
    # Render layout
    v = view.View(context=ctx)
    v.template_name = 'layout'
    return v.render()

def simple_renderer(viewname, context):
    view.View.template_path = settings['DIRNAME']+'/views'
    v = view.View(context=context)
    v.template_name = viewname
    return v.render()

def compile():   
    print('### Compiling static files...')
    print('.less files', end=", ")
    for less_file in glob.glob('static/css/*.less'):
        css_file = less_file.replace('.less','.css')
        local('node_modules/less/bin/lessc %s %s' % (less_file,css_file))
        
    #local('sass --watch static/css/:static/css/ &')
    print(".coffee files", end=", ")
    local('coffee -c -o static/js/ static/coffee')
    print()

def render():
    '''Render all the template files!'''
    print("### Rendering template files... ")
    
    views_to_stage = [
        ('app',{'settings':[settings]},renderer),
        ('pub',{'settings':[settings]},renderer),
        ('dropper',{'settings':[settings]}, simple_renderer),
        ('nodeexp',{'settings':[settings]}, renderer),
    ]
    
    if not os.path.isdir(staged_dir):
        os.mkdir(staged_dir)
    for view,context,_renderer in views_to_stage:
        print(view, end=", ")
        html = _renderer(view, context)
        open(os.path.join(staged_dir,view),'w').write(html)
    print()
    
    
def stage(prep=True):
    '''Stage all the necessary static'''
    if prep:
        compile()
        render()
    
    print('### Staging static files...')
    if not os.path.isdir(orig_static_dir):
        print("Couldn't find the static files dir...")
        return
    local('rsync -uvr %s %s' % (orig_static_dir, staged_dir))
    
    print("...Done Staging")
    
    #shutil.copytree(orig_static_dir,staged_static_dir)


def serve():
    stage()
    static_serve.serve()
