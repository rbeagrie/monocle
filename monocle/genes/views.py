# Create your views here.
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.datastructures import MultiValueDictKeyError
from django.template import RequestContext
from genes.models import Gene
import os, subprocess
temp_dir = "E:\\Rob\\Bioinformatics\\Monocle\\monocle\\genes\\static"
r_functions = "E:\\Rob\\Bioinformatics\\Monocle\\r_functions.r"
r_exec = "C:\\Program Files\\R\\R-2.13.2\\bin\\Rscript.exe"

@login_required
def index(request):

	gene_list = ['Sox2','Fgf5']
	return render_to_response('genes/index.html',{'host':request.META['HTTP_HOST']},context_instance=RequestContext(request))

@login_required
def detail(request, gene_id):
	print request.user
	if not request.user.is_authenticated():
		return render_to_response('myapp/login_error.html')
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	graph_path = os.path.join(temp_dir,'genes',gene_id+'.png')
	if not os.path.exists(graph_path):
		dostuff = subprocess.call([r_exec,r_functions,'--args','gene',gene_id,graph_path], shell = True)
	return render_to_response('genes/detail.html', {'gene' : g, 'host':request.META['HTTP_HOST']} ,context_instance=RequestContext(request))

@login_required
def tss(request, gene_id):
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	iss = g.isoform_set.all()
	tss_set = set()
	for i in iss:
		tss_set.add(i.TSS_group)
	tss_list = sorted(list(tss_set),key=lambda t:t.TSS_group_id)
	graph_path = os.path.join(temp_dir,'tss',gene_id+'.png')
	if not os.path.exists(graph_path):
		dostuff = subprocess.call([r_exec,r_functions,'--args','tss',gene_id,graph_path], shell = True)
	return render_to_response('genes/tss.html', {'gene' : g,'tss': tss_list, 'host':request.META['HTTP_HOST']},context_instance=RequestContext(request) )

@login_required
def isoforms(request, gene_id):
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	graph_path = os.path.join(temp_dir,'isoforms',gene_id+'.png')
	if not os.path.exists(graph_path):
		dostuff = subprocess.call([r_exec,r_functions,'--args','isoform',gene_id,graph_path], shell = True)
	return render_to_response('genes/isoforms.html', {'gene' : g, 'host':request.META['HTTP_HOST']} ,context_instance=RequestContext(request))

@login_required
def search(request):
	gene_id=request.GET['gene']
	try:
		g = Gene.objects.get(gene_short_name=gene_id)
	except Gene.DoesNotExist:
		return render_to_response('genes/index.html',{'error_message':'The gene %s does not exist in the database.'%gene_id} ,context_instance=RequestContext(request))
	return redirect('http://'+request.META['HTTP_HOST']+'/genes/%s/'%gene_id)
	
