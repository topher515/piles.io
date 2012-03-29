from django.db import models


class Uploader(models.Model):
    uuid = models.CharField(max_length=64)
    

class ShinyBox(models.Model):
    admin = models.ForeignKey('auth.User')
    domain = models.CharField(max_length=256,unique=True)
        

class Password(models.Model):
    pile = models.ForeignKey(ShinyBox)
    secret = models.CharField(max_length=40)
    
    
    
class File(models.Model):
    name = models.CharField(max_length=1024)
    size = models.IntegerField()
    filetype = models.CharField(max_length=32)
    uuid = models.CharField(max_length=64)
    shiny_box = models.ForeignKey(ShinyBox,related_name='files',db_index=True)
    uploader = models.ForeignKey(Uploader,related_name='uploaders')
    started_ts = models.DateTimeField(auto_now_add=True)
    success_ts = models.DateTimeField(null=True,blank=True)
    expires_ts = models.DateTimeField(db_index=True,null=True) 