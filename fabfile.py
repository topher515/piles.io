from __future__ import print_function

from fabric.api import local #, abort, run, cd, env
#from fabric.api import settings as fabsettings
#from fabric.contrib.console import confirm

import time
import os, yaml
from os.path import join as pjoin
import glob
from pystache import loader, view
import shutil
    
from piles_static import serve as static_serve

from settings import env
settings = env('development')

staged_dir = os.path.join(settings['DIRNAME'],'staged')
orig_static_dir = os.path.join(settings['DIRNAME'],'static')


## Rendering templates ###  
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

views_to_stage = {
    'app':{'context':{'settings':[settings]},'renderer':renderer},
    'pub':{'context':{'settings':[settings]},'renderer':renderer},
    'dropper':{'context':{'settings':[settings]},'renderer':simple_renderer},
    'nodeexp':{'context':{'settings':[settings]},'renderer':renderer}
}


def render(viewname=None):
    '''Render all the template files!'''
    print("### Rendering template files... ")
    
    if not os.path.isdir(staged_dir):
        os.mkdir(staged_dir)
        
    def do_render(view,context,_renderer):
        print(view, end=", ")
        html = _renderer(view, context)
        open(os.path.join(staged_dir,view),'w').write(html)
        
    if viewname:
        v = views_to_stage.get(viewname)
        if not v:
            print("Don't know how to render '%s'" % viewname)
            return
        do_render(viewname,v['context'],v['renderer'])
    else:
        for view,foo in views_to_stage.iteritems():
            do_render(view,foo['context'],foo['renderer'])
    print()



### Compiling static files ###
def compile_coffee(watch=False):
    print(".coffee files", end=", ")
    local('coffee -c%s -o static/js/ static/coffee' % ('w' if watch else ''))
    print()

def compile_less(watch=False):
    print('.less files', end=", ")
    for less_file in glob.glob('static/css/*.less'):
        css_file = less_file.replace('.less','.css')
        local('node_modules/less/bin/lessc %s %s' % (less_file,css_file))

def compile():   
    print('### Compiling static files...')  
    #local('sass --watch static/css/:static/css/ &')
    compile_less()
    compile_coffee()


    
    
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


### Watching ###
def glob_recurse_dirs(to_examine_paths, glob_suffix='*'):
    found = []
    for path in to_examine_paths:
        if os.path.isdir(path):
            found += glob_recurse_dirs(glob.glob(pjoin(path,glob_suffix)))
        else:
            found.append(path)
    return found

def poll(mods):
    for filename in glob_recurse_dirs(['static','views']):
        #print(filename)
        x = os.stat(filename).st_mtime
        if x > (mods.get(filename) or 0):
            mods[filename] = x  
            if filename.endswith('.less'):
                local('node_modules/less/bin/lessc %s %s' % (filename,'staged/'+filename.replace('.less','.css')))
            elif filename.endswith('.coffee'):
                local('coffee -c -o %s %s' % (os.path.dirname('staged/'+filename).replace('coffee','js'), filename) )
            elif filename.endswith('.mustache'):
                render(filename.split('/')[-1][:-9])
            else:
                open(os.path.join(staged_dir,filename),'w').write(open(filename,'r').read())
    return mods
                
                
    
def watch():
    mods = {}
    while True:
        mods = poll(mods)
        time.sleep(1)


def serve():
    stage()
    static_serve.serve()
