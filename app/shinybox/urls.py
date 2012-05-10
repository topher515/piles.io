from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template


from views import page, api

# Page views
urlpatterns = patterns('',
    url(r'^start/$', page.StartView.as_view(), name='start-page'),
    url(r'^login/$', page.LoginView.as_view(), name='login-page'),
    url(r'^deploy/$', page.DeployView.as_view(), name='deploy-page'),
    #url(r'^manage/(?P<pile_domain>\w\d\.-_+)/$', ManageView.as_view(), name='shinybox-manage'),
    url(r'^pay/$', page.PayView.as_view(), name='pay-page'),
    
    # XDBackbone
    url(r'^xdbackbone\.html$', direct_to_template, {'template':'xdbackbone.html'}),
)


from tastypie.api import Api
v1_api = Api(api_name='1')
v1_api.register(api.ShinyBoxResource())
v1_api.register(api.FilesResource())
v1_api.register(api.AdminResource())

urlpatterns += patterns('',
    url(r'', include(v1_api.urls)),
)