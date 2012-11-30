from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'dataset.views.index'),
    url(r'^(?P<dataset_id>[0-9]+)/$', 'dataset.views.detail'),
    url(r'^compare/(?P<sample_1_id>[0-9]+)/(?P<sample_2_id>[0-9]+)/$', 'dataset.views.compare'),
    url(r'^genes/(?P<sample_1_id>[0-9]+)/(?P<sample_2_id>[0-9]+)/page/(?P<page>[0-9]+)/$', 'dataset.views.compare_genes'),
    url(r'^genes/(?P<sample_1_id>[0-9]+)/(?P<sample_2_id>[0-9]+)/$', 'dataset.views.compare_genes'),
	

)
