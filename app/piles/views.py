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
     
     
def ensure_session(request,pile=None):
    if not request.user.is_authenticated:
        return
    if not request.session.get('pile'):
        request.session['pile'] = pile or \
            get_object_or_404(Pile, Q(admins=request.user) || Q(participants=request.user))
   

class CreatePileView(FormView):
    template_name = 'pile_create.html'
    form_class = PileForm
    def form_valid(self,form):
        data=form.cleaned_data
        user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
        pile = Pile(domain=data['domain'])
        pile.save()
        pile.admins.add(user)
        pile.save()
        user = authenticate(username=data['email'], password=data['password'])
        assert(user)
        login(request, user)
        ensure_session(request,pile)
        return HttpResponseRedirect(reverse('pile-manage',data['domain']))
        
class PileManageView(TemplateView):
    template_name = 'pile_manage.html'
    def get_context_data(self, pile_domain, *args, **kwargs):
        return {
            'pile':get_object_or_404(Pile,domain=pile_domain)
        }
        
