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

from django.core.serializers import serialize
from django.utils.simplejson import dumps, loads, JSONEncoder
from django.db.models.query import QuerySet
from django.utils.functional import curry
class DjangoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySet):
            return loads(serialize('json', obj))
        return JSONEncoder.default(self,obj)
dumps = curry(dumps, cls=DjangoJSONEncoder)


class APIView(FormView):
    
    allowed_methods = []
    
    def get_allowed_methods(self):
        return [x.upper() for x in self.allowed_methods]
    
    def box_no_auth(self, request, domain):
        domain = domain.lower()
        box = ShinyBox.objects.filter(domain=domain).select_related('files')
        if box.count() == 0:
            raise Http404
        return box[0]
        
    def box_w_auth(self, request, domain):
        domain = domain.lower()
        box = ShinyBox.objects.filter(domain=domain).select_related('files')
        if box.count() == 0:
            raise Http404
        if box[0].admin != request.user:
            raise
        return box[0]
    
    def get_cors_response(self, *args, **kwargs):
        h = HttpResponse()
        #allowed_origins = [x.strip('/') for x in settings.API_ACCESS_CONTROL_ALLOW_ORIGINS]
        #h['Access-Control-Allow-Origin'] = ', '.join(allowed_origins)
        #h['Access-Control-Allow-Method'] = ', '.join(self.get_allowed_methods())
        #h['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept'
        return h
    
    def options(self, request, *args, **kwargs):
        return self.get_cors_response()


class Files(APIView):
    
    allowed_methods = ['POST','GET','OPTIONS']
    
    def get(self, request, domain, *args, **kwargs):
        r = self.get_cors_response()
        return r.write(dumps(self.box_w_auth(request,domain).files.all()))
        
    def post(self, request):
        box = self.box_no_auth(domain)
        r = self.get_cors_response()
        file_form = FileForm(request.POST)
        if file_form.is_valid():
            _file = file_form.save()
            r.write(dumps(_file))
        else:
            r.status=400
        return r
            
        