# Create your views here.
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.datastructures import MultiValueDictKeyError
from django.template import RequestContext
from genes.models import Gene
import os, subprocess
from monocle.settings import GRAPH_DIR, R_EXEC, R_SCRIPTS
import random
import django
import datetime

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import matplotlib

@login_required
def index(request):

	return render_to_response('genes/index.html',{'host':request.META['HTTP_HOST']},context_instance=RequestContext(request))

@login_required
def detail(request, gene_id):
	print request.user
	if not request.user.is_authenticated():
		return render_to_response('myapp/login_error.html')
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	return render_to_response('genes/detail.html', {'gene' : g, 'host':request.META['HTTP_HOST']} ,context_instance=RequestContext(request))

@login_required
def tss(request, gene_id):
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	iss = g.isoform_set.all()
	tss_set = set()
	for i in iss:
		tss_set.add(i.TSS_group)
	tss_list = sorted(list(tss_set),key=lambda t:t.TSS_group_id)
	return render_to_response('genes/tss.html', {'gene' : g,'tss': tss_list, 'host':request.META['HTTP_HOST']},context_instance=RequestContext(request) )

@login_required
def isoforms(request, gene_id):
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	return render_to_response('genes/isoforms.html', {'gene' : g, 'host':request.META['HTTP_HOST']} ,context_instance=RequestContext(request))
	
@login_required
def similar(request, gene_id):
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	similar = g.get_similar()
	return render_to_response('genes/similar.html', {'gene' : g, 'similar': similar[1:11], 'host':request.META['HTTP_HOST']} ,context_instance=RequestContext(request))

@login_required
def search(request):
	gene_id=request.GET['gene']
	try:
		g = Gene.objects.get(gene_short_name__iexact=gene_id)
	except Gene.DoesNotExist:
		try:
			g = Gene.objects.get(gene_short_name__istartswith=gene_id+',')
		except Gene.DoesNotExist:
			try:
				g = Gene.objects.get(gene_short_name__iendswith=','+gene_id)
			except Gene.DoesNotExist:
				return render_to_response('genes/index.html',{'error_message':'The gene %s does not exist in the database.'%gene_id} ,context_instance=RequestContext(request))
	
	return redirect('http://'+request.META['HTTP_HOST']+'/genes/%s/' % g.gene_short_name)
	
class expression_line():
	
	def __init__(self):
		matplotlib.rc('axes',edgecolor='white')

		self.fig=Figure(figsize=(11,6))
		self.fig.set_facecolor('white')
		self.ax=self.fig.add_subplot(111)
		self.ax.set_axis_bgcolor('#EEEEEE')
		self.ax.grid(True,color='white',ls='-',lw=2,zorder=2)
		self.ax.tick_params(axis='both', direction='out')
		self.ax.get_xaxis().tick_bottom()   # remove unneeded ticks 
		self.ax.get_yaxis().tick_left()
		
		box = self.ax.get_position()
		self.ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])

		
		self.y_low = 'unset'
		self.y_high = 'unset'
		
		self.colors = ['#1F78B4','#33A02C','#E31A1C','#FF7F00','#6A3D9A','#A6CEE3','#B2DF8A','#FB9A99','#FDBF6F','#CAB2D6','#FFFF99']
		
	def add_gene(self,gene):
		
		gene_data = gene.genedata_set.all()
		
		gene_line = self.add_data(gene_data)
		for i,gd in enumerate(gene_data):
			draw_error(self.ax,i,gd.conf_lo,gd.conf_hi,color=gene_line[0].get_color())
			
		samples = map(lambda f: f.sample_name.sample_name,gene_data)
		self.ax.set_xticks(range(len(samples)))
		self.ax.set_xticklabels(samples,rotation='vertical')
		self.ax.set_ylabel('FPKM')
		self.ax.legend(gene_line,[gene.gene_short_name],loc='center left', bbox_to_anchor=(1, 0.5))
		y_low = min(map(lambda f: f.conf_lo,gene_data))
		y_high = max(map(lambda f: f.conf_hi,gene_data))
		
		self.update_y_limits(y_low,y_high)
		
	def add_tss(self,gene):
		
		tss_set = gene.tss_set.all()
		lines = []
		for tss in tss_set:
			line = self.add_data(tss.tssdata_set.all())
			lines.append(line[0])
			
		samples = map(lambda f: f.sample_name.sample_name,tss.tssdata_set.all())
		self.ax.set_xticks(range(len(samples)))
		self.ax.set_xticklabels(samples,rotation='vertical')
		self.ax.set_ylabel('FPKM')
		
		self.ax.legend(lines,map(lambda f: f.TSS_group_id,tss_set),loc='center left', bbox_to_anchor=(1, 0.5))
		
	def add_isoforms(self,gene):
		
		isoform_set = gene.isoform_set.all()
		lines = []
		for isoform in isoform_set:
			line = self.add_data(isoform.isoformdata_set.all())
			lines.append(line[0])
			
		samples = map(lambda f: f.sample_name.sample_name,isoform.isoformdata_set.all())
		self.ax.set_xticks(range(len(samples)))
		self.ax.set_xticklabels(samples,rotation='vertical')
		self.ax.set_ylabel('FPKM')
		
		self.ax.legend(lines,map(lambda f: f.nearest_ref_id,isoform_set),loc='center left', bbox_to_anchor=(1, 0.5))
		
	def add_data(self,gene_data):
	
		fpkms = map(lambda f: f.fpkm,gene_data)
		x=range(len(fpkms))
		y=fpkms
		gene_line = self.ax.plot(x,y,zorder=10,label='Gene',color=self.colors.pop(0))
		
		self.ax.set_xlim(-0.5,len(fpkms)-0.5)
		
		y_low = min(fpkms)
		y_high = max(fpkms)
		
		self.update_y_limits(y_low,y_high)
		
		return gene_line
		
	def update_y_limits(self,new_low,new_high):
		if self.y_low == 'unset':
			self.y_low = new_low
		elif self.y_low > new_low:
			self.y_low = new_low
		
		if self.y_high == 'unset':
			self.y_high = new_high
		elif self.y_high < new_high:
			self.y_high = new_high
		
		self.ax.set_ylim(self.y_low-0.5,self.y_high+0.5)
	
	
def gene_graph(request, gene_id):
	
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	
	graph = expression_line()
	graph.add_gene(g)
		
	graph.ax.set_title(gene_id)
	
	canvas=FigureCanvas(graph.fig)
	response=django.http.HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response	
	
def tss_graph(request, gene_id):
	
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	
	print g.tss_set.all()
	
	graph = expression_line()
	graph.add_tss(g)
		
	graph.ax.set_title(gene_id)
	
	canvas=FigureCanvas(graph.fig)
	response=django.http.HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response
	
def isoform_graph(request, gene_id):
	
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	
	print g.isoform_set.all()
	
	graph = expression_line()
	graph.add_isoforms(g)
		
	graph.ax.set_title(gene_id)
	
	canvas=FigureCanvas(graph.fig)
	response=django.http.HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response
	
def draw_error(axes,x,y_low,y_high,color,bar_width=0.1):
	v_line = matplotlib.lines.Line2D([x,x],[y_low,y_high],zorder=20,color=color)
	top_h = matplotlib.lines.Line2D([x-bar_width,x+bar_width],[y_high,y_high],zorder=20,color=color)
	bottom_h = matplotlib.lines.Line2D([x-bar_width,x+bar_width],[y_low,y_low],zorder=20,color=color)
	axes.add_line(v_line)
	axes.add_line(top_h)
	axes.add_line(bottom_h)
