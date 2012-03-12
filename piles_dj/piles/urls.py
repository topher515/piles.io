from django.conf.urls.defaults import patterns, include, url

from views import *

urlpatterns = patterns('',
    url(r'^create/$', PileCreateView.as_view(), name='pile-create'),
    url(r'^manage/(?P<pile_domain>\w\d\.-_+)/$', PileManageView.as_view(), name='pile-manage'),
)
