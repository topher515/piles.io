from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import CreateView, FormView
#from django.views.generic.list_detail import object_list
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, UserManager
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from django.conf import settings
  
  
from shinybox.forms import *
from shinybox.models import *

from contentstore import S3Store as ContentStore

from django.core.serializers import serialize
import django.utils.simplejson as json
from django.db.models.query import QuerySet
from django.utils.functional import curry
class DjangoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySet):
            return json.loads(serialize('json', obj))
        return json.JSONEncoder.default(self,obj)
dumps = curry(json.dumps, cls=DjangoJSONEncoder)


class APIMixin(object):
    
    allowed_methods = []
    
    def get_allowed_methods(self):
        return [x.upper() for x in self.allowed_methods]
    
    def get_box(self, request, domain):
        domain = domain.lower()
        box = ShinyBox.objects.filter(domain=domain).select_related('files')
        if box.count() == 0:
            raise Http404
        return box[0]
    
    box_no_auth = get_box
    
    def box_w_auth(self, request, domain):
        box = self.get_box(request, domain)
        if box[0].admin != request.user:
            raise
        return box[0]
    
    def ensure_uploader(self, request):
        if not request.session.get('uploader'):
            u = Uploader()
            u.save()
            request.session['uploader'] = u
    
    def get_cors_response(self, *args, **kwargs):
        h = HttpResponse()
        #allowed_origins = [x.strip('/') for x in settings.API_ACCESS_CONTROL_ALLOW_ORIGINS]
        #h['Access-Control-Allow-Origin'] = ', '.join(allowed_origins)
        #h['Access-Control-Allow-Method'] = ', '.join(self.get_allowed_methods())
        #h['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept'
        return h
    
    def options(self, request, *args, **kwargs):
        return self.get_cors_response()


class Files(FormView, APIMixin):
    
    allowed_methods = ['POST','GET','OPTIONS']
    
    def get(self, request, domain, *args, **kwargs):
        self.ensure_uploader(request)
        r = self.get_cors_response()
        return r.write(dumps(self.box_w_auth(request,domain).files.all()))
        
    def post(self, request, domain, *args, **kwargs):
        self.ensure_uploader(request)
        box = self.box_no_auth(request,domain)
        r = self.get_cors_response()
        file_form = FileForm(json.load(request))
        if file_form.is_valid():
            _file = file_form.save(commit=False)
            _file.uploader = request.session['uploader']
            _file.bucket = box
            _file.save()
            r.write(dumps(f))
        else:
            r.status_code=400
            r.write(dumps(file_form.errors))
        return r


import re
from piston.handler import BaseHandler
from piston.utils import rc, throttle

class FilesHandler(BaseHandler, APIMixin):

    allowed_methods = ('GET', 'POST')
    #fields = ('name','filetype','size')
    exclude = ('id','bucket','uploader')
    model = File
    
    
    def read(self,request,domain):
        self.ensure_uploader(request)
        r = self.get_cors_response()
        fs = self.box_w_auth(request,domain).files.all()
        print fs
        return fs 
          
    def create(self,request,domain):
        self.ensure_uploader(request)
        box = self.box_no_auth(request,domain)
        r = self.get_cors_response()
        file_form = FileForm(json.load(request))
        if file_form.is_valid():
            _file = file_form.save(commit=False)
            _file.uploader = request.session['uploader']
            _file.bucket = box
            _file.save()
            f = dict(_file.__dict__)
            f['key'] = f['uuid']
            f = ContentStore(\
                s3conn=(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY),
                bucket=settings.STATIC_BUCKET,
                bucket_acl=settings.STATIC_BUCKET_ACL
            ).add_storage_info(f)
            return f
        else:
            r = rc.BAD_REQUEST
            r.write(dumps(file_form.errors))
            return r
    