from django.conf.urls.defaults import patterns, include, url

from views import api, page

urlpatterns = patterns('',
    # Page views
    url(r'^start/$', page.StartView.as_view(), name='shinybox-start'),
    url(r'^deploy/$', page.DeployView.as_view(), name='shinybox-deploy'),
    #url(r'^manage/(?P<pile_domain>\w\d\.-_+)/$', ManageView.as_view(), name='shinybox-manage'),
    
    # API views
    url(r'^buckets/(?P<domain>[\w\d_-]+)/files/$', api.Files.as_view())
)
