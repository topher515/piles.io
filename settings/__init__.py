import os
import yaml


defaults = yaml.load(open('settings/base.yml','r'))
production = {}
production.update(defaults)
production.update(yaml.load(open('settings/production.yml','r')))
development = {}
development.update(defaults)

settings = None


def env(env_name):
    global settings
    if not settings:
        settings = globals()[env_name]
        
    return settings
        
    
    
    
   
    