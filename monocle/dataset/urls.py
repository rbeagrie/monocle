from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'dataset.views.index'),
    url(r'^(?P<dataset_id>[0-9]+)/$', 'dataset.views.detail'),
    url(r'^compare/(?P<sample_1_id>[0-9]+)/(?P<sample_2_id>[0-9]+)/$', 'dataset.views.compare'),
	

)
