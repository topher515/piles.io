from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView, TemplateResponseMixin, View
from django.views.generic.edit import CreateView, FormView
#from django.views.generic.list_detail import object_list
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, UserManager
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
import json
   
from shinybox.forms import *
from shinybox.models import *

import stripe
stripe.api_key = "vtUQeOtUnYr7PGCLQ96Ul4zqpDUO4sOE"

class StripeWebhook(View):
    def post(self):
        event = stripe.Event(json.loads(self.request.body))
        handler = "handle_%s" % (event.type.replace('.','_'))
        handler_func = getattr(self,handler,None)
        return handler_func()
        
