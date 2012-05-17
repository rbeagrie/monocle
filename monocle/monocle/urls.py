from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
	url(r'^genes/$', 'genes.views.index'),
	url(r'^genes/search/$', 'genes.views.search'),
	url(r'^genes/login/$', 'django.contrib.auth.views.login', {'template_name': 'genes/login.html'}),
	url(r'^genes/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^genes/(?P<gene_id>\w+)/$', 'genes.views.detail'),
    url(r'^genes/(?P<gene_id>\w+)/tss/$', 'genes.views.tss'),
    url(r'^genes/(?P<gene_id>\w+)/isoforms/$', 'genes.views.isoforms'),
    url(r'^genes/(?P<gene_id>\w+)/similar/$', 'genes.views.similar'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
