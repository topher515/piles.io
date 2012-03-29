from django.db import models

class Uploader(models.Model):
    uuid = models.CharField(max_length=64)

#class FacebookVerified(models.Model):
#    user = models.ForeignKey('auth.User', related_name='verified_facebook')
#
#class TwitterVerified(models.Model):
#    user = models.ForeignKey('auth.User', related_name='verified_twitter')
#
#class EmailVerified(models.Model):
#    user = models.ForeignKey('auth.User', related_name='verified_email')


class Pile(models.Model):
    admins = models.ManyToManyField('auth.User', related_name='admin_piles')
    participants = models.ManyToManyField('auth.User',related_name='participant_piles')
    domain = models.CharField(max_length=256,unique=True)
    name = models.CharField(max_length=256,blank=True)

    def is_authorized(self,user):
        
        

class Password(models.Model):
    pile = models.ForeignKey(Pile, related_name='authorizor_password')
    secret = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(blank=True,null=True)

class Facebook(models.Model):
    pile = models.ForeignKey(Pile, related_name='authorizor_password')
    secret = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(blank=True,null=True)

    
    
class File(models.Model):
    name = models.CharField(max_length=1024)
    size = models.IntegerField()
    filetype = models.CharField(max_length=32)
    uuid = models.CharField(max_length=64)
    pile = models.ForeignKey(Pile,related_name='files')
    uploader = models.ForeignKey(Uploader,related_name='uploads')
    created = models.DateTimeField(auto_now_add=True)
    success = models.DateTimeField(null=True,blank=True)
    path = models.CharField(max_length=1024,blank=True)
    
