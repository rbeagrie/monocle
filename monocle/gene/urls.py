from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    # Examples:
	url(r'^$', 'gene.views.index'),
	url(r'^search/$', 'gene.views.search'),
    url(r'^(?P<gene_id>[0-9\,]+)/$', 'gene.views.detail'),
    url(r'^(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/tss/$', 'gene.views.tss'),
    url(r'^(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/isoforms/$', 'gene.views.isoforms'),
    url(r'^(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/similar/$', 'gene.views.similar'),
	
)