from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    # Examples:
    url(r'^list/(?P<list_id>[0-9]+)/dataset/(?P<dataset_id>[0-9\,]+)/graph.png$', 'graph.views.list'),
    url(r'^gene/(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/graph.png$', 'graph.views.gene'),
    url(r'^gene/(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/tss/graph.png$', 'graph.views.tss'),
    url(r'^gene/(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/isoforms/graph.png$', 'graph.views.isoform'),
    url(r'^dataset/(?P<dataset_id>[0-9\,]+)/graph.png$', 'graph.views.dataset'),

)
