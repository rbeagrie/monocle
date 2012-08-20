from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
	url(r'^genes/$', 'genes.views.index'),
	url(r'^genes/search/$', 'genes.views.search'),
	url(r'^genes/upload/$', 'genes.views.upload_genelist'),
	url(r'^genes/handle_list/$', 'genes.views.handle_list'),
    url(r'^genes/lists/$', 'genes.views.show_lists'),
    url(r'^genes/lists/(?P<list_id>[0-9]+)/$', 'genes.views.list_detail'),
    url(r'^genes/lists/(?P<list_id>[0-9]+)/dataset/(?P<dataset_id>[0-9\,]+)/graph.png$', 'genes.views.list_graph'),
    url(r'^genes/lists/(?P<list_id>[0-9]+)/heat.png$', 'genes.views.list_heat'),
	url(r'^genes/login/$', 'django.contrib.auth.views.login', {'template_name': 'genes/login.html'}),
	url(r'^genes/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^genes/(?P<gene_id>[0-9\,]+)/$', 'genes.views.detail'),
    url(r'^genes/(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/tss/$', 'genes.views.tss'),
    url(r'^genes/(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/isoforms/$', 'genes.views.isoforms'),
    url(r'^genes/(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/similar/$', 'genes.views.similar'),
    url(r'^genes/(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/graph.png$', 'genes.views.gene_graph'),
    url(r'^genes/(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/tss/graph.png$', 'genes.views.tss_graph'),
    url(r'^genes/(?P<gene_id>[0-9\,]+)/dataset/(?P<dataset_id>[0-9\,]+)/isoforms/graph.png$', 'genes.views.isoform_graph'),
	

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
