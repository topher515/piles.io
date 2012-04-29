from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import CreateView, FormView
#from django.views.generic.list_detail import object_list
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from django.conf import settings
from django.conf.urls.defaults import url #patterns, include, 
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
  
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
        if box.admin != request.user:
            raise
        return box
    
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



from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from tastypie import fields
from tastypie.serializers import Serializer

from shinybox.auth import FilesAuthorization

class MixMe(object):
    def ensure_uploader(self, request):
        if not request.session.get('uploader'):
            u = Uploader()
            u.save()
            request.session['uploader'] = u
    

class AdminResource(ModelResource):
    class Meta:
        resource_name = 'admins'
        queryset = User.objects.all()
        serializer = Serializer(formats=['json', 'jsonp'], \
            content_types = {'json': 'application/json', 'jsonp': 'text/javascript'})
        fields = ['username', 'first_name', 'last_name']
        allowed_methods = ['get']
        #authentication = ApiKeyAuthentication()
        authorization = Authorization()
        

class ShinyBoxResource(ModelResource):
    class Meta:
        resource_name = 'buckets'
        queryset = ShinyBox.objects.all()
        serializer = Serializer(formats=['json', 'jsonp'], \
            content_types = {'json': 'application/json', 'jsonp': 'text/javascript'})
        #authentication = ApiKeyAuthentication()
        authorization = Authorization()
        filtering = {
            #'pub_date': ['exact', 'lt', 'lte', 'gte', 'gt'],
            'domain': ALL
        }
    
    admin = fields.ToOneField(AdminResource, 'admin', full=True)
    files = fields.ToManyField('shinybox.views.api.FilesResource', 'files')
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<domain>\w[\w-]*)/$" % self._meta.resource_name, 
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
#            url(r"^(?P<resource_name>%s)/(?P<domain>\w[\w-]*)/files%s$" % (self._meta.resource_name, trailing_slash()), 
#                self.wrap_view('files_dispatch_list'), name="api_files_dispatch_list"),
        ]
        
    
#    def files_dispatch_list(self, request, domain, **kwargs):
#        try:
#            obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
#        except ObjectDoesNotExist:
#            return HttpGone()
#        except MultipleObjectsReturned:
#            return HttpMultipleChoices("More than one resource is found at this URI.")
#    
#        files_resource = FilesResource(bucket_domain=domain)
#        return files_resource.dispatch_list(request)
    

class FilesResource(ModelResource, MixMe):
    
    def __init__(self,*args,**kwargs):
        #self._bucket_domain = kwargs.pop('bucket_domain',None)
        super(FilesResource,self).__init__(*args,**kwargs)
    
    bucket = fields.ToOneField(ShinyBoxResource, 'bucket')
    
    class Meta:
        resource_name = 'files'
        queryset = File.objects.all()
        #authentication = ApiKeyAuthentication()
        authorization = FilesAuthorization()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete', 'put']

        filtering = {
            'bucket': ALL_WITH_RELATIONS,
            'name': ALL,
        }

    #bucket = fields.ToOneField(ShinyBoxResource, 'bucket')
  
    #def dipatch_list(self, request, **kwargs):
    #    self._bucket_domain = kwargs.pop('domain')
    #    return super(FilesResource, self).dispatch_list(request,kwargs)
        
    #def get_object_list(self, request):
    #    obj_list = super(FilesResource, self).get_object_list(request)
    #    return obj_list.filter(bucket__domain=self._bucket_domain)
  
    def dispatch(self, request_type, request, **kwargs):
        print "File kwargs: %s" % kwargs
        self.ensure_uploader(request)
        return super(FilesResource,self).dispatch(request_type, request, **kwargs)

    def obj_create(self, bundle, request, **kwargs):
        #bundle.obj.bucket = ShinyBox.objects.get(domain=self._bucket_domain)
        #bucket = ShinyBox.objects.get(domain=self._bucket_domain)
        #print bundle.obj
        #print bundle.data
        #bundle.data['bucket_id'] = ShinyBox.objects.get(domain=self._bucket_domain).id
        #print bundle
        #print bundle.obj
        #print bundle.data
        #kwargs['bucket'] = ShinyBox.objects.get(domain=request.POST.get('bucket'))
        
        kwargs["path"] = "inbox"
        return super(FilesResource,self).obj_create(bundle, request, **kwargs)

    def hydate(self, bundle):
        bundle.obj.bucket = ShinyBox.objects.get(domain=bundle.data.pop('bucket'))
        print bundle
        return bundle

    def alter_detail_data_to_serialize(self, request, data):
        if request.POST:
            data = ContentStore(\
                s3conn=(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY),
                bucket=settings.STATIC_BUCKET,
                bucket_acl=settings.STATIC_BUCKET_ACL
            ).add_storage_info(data)
        return super(FilesResource,self).alter_detail_data_to_serialize(request,data)

    #def post_list(self, request, **kwargs):
    #    self.ensure_uploader(request)
    #    #box = self.box_no_auth(request,domain)
    #    return super(FilesResource,self).post_list(request,**kwargs)
        

    