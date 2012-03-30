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
    def box_no_auth(self, domain):
        domain = domain.lower()
        box = ShinyBox.objects.filter(domain=domain).select_related('files')
        if box.count() == 0:
            raise Http404
        return box[0]
        
    def box_w_auth(self, domain):
        domain = domain.lower()
        box = ShinyBox.objects.filter(domain=domain).select_related('files')
        if box.count() == 0:
            raise Http404
        if box[0].admin != request.user:
            raise
        return box[0]
        

class Files(APIView):
    def get(self, request, domain):
        return HttpResponse(dumps(self.box_w_auth(domain).files.all()))
        
    def post(self, request):
        box = self.box_no_auth(domain)
        file_form = FileForm(request.POST)
        if file_form.is_valid():
            file_form.save()
        return HttpResponse(dumps())
        