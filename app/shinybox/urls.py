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

#blogpost_resource = Resource(handler=BlogPostHandler, **ad)
#arbitrary_resource = Resource(handler=ArbitraryDataHandler, **ad)
tempfiles_resource = Resource(handler=api.TempFilesHandler)
files_resource = Resource(handler=api.FilesHandler)

# API handlers
urlpatterns += patterns('',
    url(r'^1/buckets/(?P<domain>[^/]+)/tempfiles/$', tempfiles_resource),
    #url(r'^posts/(?P<post_slug>[^/]+)/$', blogpost_resource), 
    #url(r'^other/(?P<username>[^/]+)/(?P<data>.+)/$', arbitrary_resource), 
)
