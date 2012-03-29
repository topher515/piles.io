from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, FormView
#from django.views.generic.list_detail import object_list
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, UserManager
from django.http import HttpResponseRedirect
from django.core.url_resolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404
   
from forms import *
from models import *
   


class StartView(FormView):
    template_name = 'shinybox_start.html'
    form_class = StartForm
    def form_valid(self,form):
        data=form.cleaned_data
        user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
        box = ShinyBox(domain=data['domain'],admin=user)
        box.save()
        user = authenticate(username=data['email'], password=data['password'])
        assert(user)
        login(request, user)
        return HttpResponseRedirect(reverse('shinybox-deploy'))
        
 
class DeployView(FormView):
    template_name = 'shinybox_deploy.html'
    form_class = DeployForm
    def form_valid(self,form):
        data=form.cleaned_data
        user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
        box = ShinyBox(domain=data['domain'],admin=user)
        box.save()
        user = authenticate(username=data['email'], password=data['password'])
        assert(user)
        login(request, user)
        return HttpResponseRedirect(reverse('shinybox-deploy'))

        
        
class ManageView(TemplateView):
    template_name = 'shinybox_manage.html'
    def get_context_data(self, pile_domain, *args, **kwargs):
        return {
            'shiny_box':get_object_or_404(ShinyBox,domain=pile_domain)
        }
        
