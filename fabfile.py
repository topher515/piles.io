from __future__ import print_function

from fabric.api import local #, abort, run, cd, env
#from fabric.api import settings as fabsettings
#from fabric.contrib.console import confirm

import time
import os, yaml
from os.path import join as pjoin
import glob
import shutil
import pystache

from settings import env
settings = env('development')

STAGE_DIR = 'staged/'

def ensure_dir(outfile):
    try:
        os.makedirs(os.path.dirname(outfile))
    except OSError as e:
        if '[Errno 17]' not in str(e):
            raise


def stache_compile(inpath,outpath):
    out = pystache.render(open(inpath,'r').read(),{'settings':settings})
    open(outpath,'w').write(out)

### Watching ###
def glob_recurse_dirs(to_examine_paths, glob_suffix='*'):
    found = []
    for path in to_examine_paths:
        if os.path.isdir(path):
            found += glob_recurse_dirs(glob.glob(pjoin(path,glob_suffix)))
        else:
            found.append(path)
    return found


def stage(compile_ts={}):
    """ Compile files. `compile_ts` is a dictionary whos keys are the paths to files and
    there last compile time (as returned by `os.stat(...).st_mtime) if the file's
    current `st_mtime` is greater than the one listed in `compile_ts` then the file is recompiled.
    
    Returns the modified dict `compile_ts`.
    """
    for filename in glob_recurse_dirs(['assets']):
        #print(filename)
        x = os.stat(filename).st_mtime
        if x > (compile_ts.get(filename) or 0):
            compile_ts[filename] = x  
            if filename.endswith('.less'):
                local('lessc %s %s' % (filename,STAGE_DIR+filename\
                    .replace('assets/','').replace('.less','.css')))
            elif filename.endswith('.coffee'):
                local('coffee -c -o %s %s' % (os.path.dirname(STAGE_DIR+filename)\
                    .replace('assets/','').replace('coffee','js'), filename) )
            elif filename.endswith('.mustache'):
                outfile = STAGE_DIR + filename.replace('assets/','')[:-9]
                ensure_dir(outfile)
                stache_compile(filename, outfile)
            else:
                outfile = os.path.join(STAGE_DIR,filename).replace('assets/','')
                ensure_dir(outfile)
                open(outfile,'w').write(open(filename,'r').read())
    return compile_ts
                
                
    
def watch():
    compile_ts = {}
    while True:
        compile_ts = stage(compile_ts)
        time.sleep(1)

