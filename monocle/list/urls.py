from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'list.views.index'),
	url(r'^handle/$', 'list.views.handle'),
	url(r'^upload/$', 'list.views.upload'),
    url(r'^(?P<list_id>[0-9]+)/$', 'list.views.detail'),
	

)