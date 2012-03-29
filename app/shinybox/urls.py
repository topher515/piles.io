from django.conf.urls.defaults import patterns, include, url

from views import *

urlpatterns = patterns('',
    url(r'^start/$', StartView.as_view(), name='shinybox-start'),
    url(r'^deploy/$', DeployView.as_view(), name='shinybox-deploy'),
    url(r'^manage/(?P<pile_domain>\w\d\.-_+)/$', ManageView.as_view(), name='shinybox-manage'),
)
