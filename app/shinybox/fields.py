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
