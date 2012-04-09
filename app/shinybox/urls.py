from django.conf.urls.defaults import patterns, include, url

from django.views.generic.simple import direct_to_template

from piston.resource import Resource
#from piston.authentication import HttpBasicAuthentication

from views import page, api
#from handlers import BlogPostHandler, ArbitraryDataHandler

# Page views
urlpatterns = patterns('',
    url(r'^start/$', page.StartView.as_view(), name='shinybox-start'),
    url(r'^deploy/$', page.DeployView.as_view(), name='shinybox-deploy'),
    #url(r'^manage/(?P<pile_domain>\w\d\.-_+)/$', ManageView.as_view(), name='shinybox-manage'),
    
    # XDBackbone
    url(r'^xdbackbone\.html$', direct_to_template, {'template':'xdbackbone.html'}),
)


#auth = HttpBasicAuthentication(realm="My Realm")
#kwargs = { 'authentication': auth }

files_resource = Resource(handler=api.FilesHandler)

# API handlers
urlpatterns += patterns('',
    url(r'^2/buckets/(?P<domain>[^/]+)/files/$', files_resource),
)

from tastypie.api import Api
v1_api = Api(api_name='1')
v1_api.register(api.ShinyBoxResource())
v1_api.register(api.FilesResource())
v1_api.register(api.AdminResource())

urlpatterns += patterns(''
    url(r'^$', includes(v1_api.urls)),
)