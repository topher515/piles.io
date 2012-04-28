from django.db import models
import uuid
from datetime import datetime, timedelta

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^shinybox\.models\.UUIDField"])
add_introspection_rules([], ["^shinybox\.models\.ExpiresDateTimeField"])

class UUIDField(models.CharField) :
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64 )
        kwargs['blank'] = True
        models.CharField.__init__(self, *args, **kwargs)
    
    def pre_save(self, model_instance, add):
        if add :
            value = str(uuid.uuid4())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, add)


class ExpiresDateTimeField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs['db_index'] = kwargs.get('db_index', True)
        kwargs['blank'] = True
        self.expires = kwargs.get('expires',60*60*24*7) # Default is seven days
        super(ExpiresDateTimeField,self).__init__(*args,**kwargs)
        
    def pre_save(self, model_instance, add):
        if add:
            value = datetime.now() + timedelta(seconds=self.expires)
            setattr(model_instance, self.attname, value) 
        return super(ExpiresDateTimeField,self).pre_save(model_instance,add)
            

        
class Uploader(models.Model):
    uuid = UUIDField(primary_key=True, editable=False)
    expires_ts = ExpiresDateTimeField()
    

class ShinyBox(models.Model):
    admin = models.ForeignKey('auth.User')
    domain = models.CharField(max_length=256,unique=True)
        
    def __repr__(self):
        return "ShinyBox(domain='%s')" % self.domain
    def __str__(self):
        return "Shinybox: %s" % self.domain

class Password(models.Model):
    pile = models.ForeignKey(ShinyBox)
    secret = models.CharField(max_length=40)
    
    
class File(models.Model):
    name = models.CharField(max_length=1024)
    size = models.IntegerField()
    filetype = models.CharField(max_length=32)
    uuid = UUIDField(primary_key=True, editable=False)
    bucket = models.ForeignKey(ShinyBox,related_name='files',db_index=True)
    uploader = models.ForeignKey(Uploader,related_name='files',null=True,blank=True)
    started_ts = models.DateTimeField(auto_now_add=True)
    success_ts = models.DateTimeField(null=True,blank=True)
    expires_ts = ExpiresDateTimeField(db_index=True,null=True)
    path = models.CharField(max_length=1024, default='inbox')