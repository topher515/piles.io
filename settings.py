import os
import yaml

class Settings(object):
    def __init__(self):
        self.conf_set = set()
        self.confs = []
        self.ignores = []
        self.requires = []
        
    def ignore(self,conf_name):
        self.ignores.append(conf_name)
        
    def require(self,conf_name):
        self.requires.append(conf_name)
        
    def add_conf(self,conf,conf_name):
        if conf_name in self.conf_set:
            return
        self.conf_set.add(conf_name)
        self.confs.append((conf,conf_name))
    
    def __call__(self,name):
        for conf,conf_name in reversed(self.confs):
            if conf_name in self.ignores:
                continue
            if len(self.requires) > 0 and conf_name not in self.requires:
                continue
                
            if conf.get(name,None) is not None:
                return conf[name]
        raise AttributeError
settings = Settings()

settings.add_conf(yaml.load(open('settings.yml','r')),'global')    

try:
	from local_settings import conf
	settings.add_conf(conf,'local')
except ImportError:
	pass # It's cool if there's no local_Settings module