from django.db import models
import uuid
from datetime import datetime, timedelta

from fields import UUIDField, ExpiresDateTimeField

import stripe
stripe.api_key = "Ndzrlauz734dK6xG5PKhk3LfLy1EQEKs"   

            
class Customer(models.Model):
    user = models.OneToOneField('auth.User')
    external_id = models.CharField(max_length=32)
    status = models.CharField(max_length=10,default='trialing')
        
    STATUS_OK = ('trialing','active','past_due')
    STATUS_BAD = ('canceled','unpaid')
    
    objects = CustomerManager()
    
    def get_stripe_customer(self):
        if not self._stripe_cust_cache:
            self._stripe_cust_cache = stripe.Customer.retrieve(self.external_id)
        return self._stripe_cust_cache
        
    def is_current(self,remote=False):
        if not self.status or remote:
            self.status = self.get_stripe_customer().subscription.status
        return self.status in Customer.STATUS_OK
        
    def get_subscription(self):
        return self.get_stripe_customer().subscription
        
    def get_plan(self):
        return self.get_subscription().plan
        
        
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
    
    def __str__(self):
        return "%s (%s)" % (self.name, self.started_ts)