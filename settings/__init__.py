import os
import yaml

settings = yaml.load(open('settings/env.yml','r'))
print "Loading environment settings '%s'..." % settings,
for env in settings['ENVIRONMENT']:
    print "%s, " % env,
    e = yaml.load(open('settings/'+env+'.yml','r'))
    settings.update(e)
print 