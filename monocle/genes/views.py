# Create your views here.
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.datastructures import MultiValueDictKeyError
from django.template import RequestContext
from django.core.files.temp import TemporaryFile
from genes.models import Gene, GeneList
import os, subprocess, numpy
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
	
@login_required
def gene_graph(request, gene_id):
	
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	
	graph = expression_line()
	graph.add_gene(g)
		
	graph.ax.set_title(gene_id)
	
	return graph.response(errors=True)	

@login_required	
def tss_graph(request, gene_id):
	
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	
	graph = expression_line()
	graph.add_tss(g)
		
	graph.ax.set_title(gene_id)
	
	return graph.response()

@login_required	
def isoform_graph(request, gene_id):
	
	g = get_object_or_404(Gene, gene_short_name=gene_id)
	
	graph = expression_line()
	graph.add_isoforms(g)
		
	graph.ax.set_title(gene_id)
	
	return graph.response()

@login_required
def show_lists(request):
	l = GeneList.objects.filter(temp=False)
	return render_to_response('genes/lists.html',{'host':request.META['HTTP_HOST'],'lists':l},context_instance=RequestContext(request))
	
@login_required	
def upload_genelist(request):

	return render_to_response('genes/upload.html',{'host':request.META['HTTP_HOST']},context_instance=RequestContext(request))
	
@login_required
def handle_list(request):
	if request.method == 'POST':
		file_data = request.FILES['list'].read()
		gene_names = map(lambda s:s.strip(),file_data.split('\n'))
		temp_list = GeneList()
		temp_list.name = request.POST['name']
		if temp_list.name != '':
			temp_list.temp = False
		temp_list.save()
		not_found = []
		
		for gene_name in gene_names:
			try:
				g = Gene.objects.get(gene_short_name__iexact=gene_name)
				temp_list.genes.add(g)
			except Gene.DoesNotExist:
				try:
					g = Gene.objects.get(gene_short_name__istartswith=gene_name+',')
					temp_list.genes.add(g)
				except Gene.DoesNotExist:
					try:
						g = Gene.objects.get(gene_short_name__iendswith=','+gene_name)
						temp_list.genes.add(g)
					except Gene.DoesNotExist:
						not_found.append(gene_name)
		temp_list.save()
		genes = temp_list.genes.all()
		if len(not_found):
			return render_to_response('genes/handle_list.html',{'host':request.META['HTTP_HOST'],
																'gene_list':genes,
																'genes_matched':len(genes),
																'not_found':not_found,
																'not_matched':len(not_found),
																'list_id':temp_list.pk},context_instance=RequestContext(request))
		else:
			return redirect('http://'+request.META['HTTP_HOST']+'/genes/lists/'+str(temp_list.pk))
	else:
		return redirect('http://'+request.META['HTTP_HOST']+'/genes/upload/')
		
@login_required	
def list_detail(request, list_id):
	
	l = get_object_or_404(GeneList, pk=list_id)
	print l.genes.count()
	if l.genes.count() > 10:
		heat = True
	else:
		heat = False
	
	return render_to_response('genes/list_detail.html',{'host':request.META['HTTP_HOST'],'list':l,'heat':heat},context_instance=RequestContext(request))

def list_graph(request, list_id):

	l = get_object_or_404(GeneList, pk=list_id)
	genes = l.genes.all()
	
	graph = expression_line()
	
	for gene in genes:
		graph.add_gene(gene)
		
	graph.ax.set_title('List #%i - %s' % (l.pk,l.name))
	
	return graph.response()
	
def list_heat(request, list_id):

	l = get_object_or_404(GeneList, pk=list_id)
	genes = l.genes.all()
	
	graph = expression_heat(height=len(genes))
	
	for gene in genes:
		graph.add_gene(gene)
		
	graph.ax.set_title('List #%i - %s' % (l.pk,l.name))
	
	return graph.response()
		
class expression_line():
	
	def __init__(self):
		matplotlib.rc('axes',edgecolor='white')

		self.fig=Figure(figsize=(13,6))
		self.fig.set_facecolor('white')
		self.ax=self.fig.add_subplot(111)
		self.ax.set_axis_bgcolor('#EEEEEE')
		self.ax.grid(True,color='white',ls='-',lw=2,zorder=2)
		self.ax.tick_params(axis='both', direction='out')
		self.ax.get_xaxis().tick_bottom()   # remove unneeded ticks 
		self.ax.get_yaxis().tick_left()
		self.legend_entries = {}
		self.y_lows = []
		self.y_highs = []
		self.errors = []
		
		box = self.ax.get_position()
		self.ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])

		
		self.y_low = 'unset'
		self.y_high = 'unset'
		
		self.colors = ['#1F78B4','#33A02C','#E31A1C','#FF7F00','#6A3D9A','#A6CEE3','#B2DF8A','#FB9A99','#FDBF6F','#CAB2D6','#FFFF99']
		self.color_index = 0
		
	def next_color(self):
		col = self.colors[self.color_index % len(self.colors)]
		self.color_index += 1
		return col
		
	def add_gene(self,gene):
		
		gene_data = gene.genedata_set.all()
		
		gene_line = self.add_data(gene_data)
		self.legend_entries[gene.gene_short_name] = gene_line
		
		for i,gd in enumerate(gene_data):
		
			self.errors.append((i,gd.conf_lo,gd.conf_hi,gene_line.get_color()))
		
	def response(self,errors=False):
		self.ax.set_xticks(range(len(self.x_labels)))
		self.ax.set_xticklabels(self.x_labels,rotation='vertical')
		self.ax.set_ylabel('FPKM')
		
		self.ax.legend(self.legend_entries.values(),self.legend_entries.keys(),loc='center left', bbox_to_anchor=(1, 0.5))
		
		if errors:
			for i in range(len(self.errors)):
				self.draw_error(*self.errors[i])
			y_low = min(self.y_lows)
			y_high = max(self.y_highs)
			
			self.update_y_limits(y_low,y_high)
		canvas=FigureCanvas(self.fig)
		response=django.http.HttpResponse(content_type='image/png')
		canvas.print_png(response)
		return response
		
	def add_tss(self,gene):
		
		tss_set = gene.tss_set.all()
		
		for tss in tss_set:
			line = self.add_data(tss.tssdata_set.all())
			self.legend_entries[tss.pk] = line
		
	def add_isoforms(self,gene):
		
		isoform_set = gene.isoform_set.all()
		
		for isoform in isoform_set:
			line = self.add_data(isoform.isoformdata_set.all())
			self.legend_entries[isoform.nearest_ref_id] = line
		
		
	def add_data(self,gene_data):
	
		self.x_labels = map(lambda f: f.sample_name.sample_name,gene_data)
		self.y_lows.extend(map(lambda f: f.conf_lo,gene_data))
		self.y_highs.extend(map(lambda f: f.conf_hi,gene_data))

		fpkms = map(lambda f: f.fpkm,gene_data)
		x=range(len(fpkms))
		y=fpkms
		gene_line = self.ax.plot(x,y,zorder=10,label='Gene',color=self.next_color())
		
		self.ax.set_xlim(-0.5,len(fpkms)-0.5)
		
		y_low = min(fpkms)
		y_high = max(fpkms)
		
		self.update_y_limits(y_low,y_high)
		
		return gene_line[0]
		
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
	
	def draw_error(self,x,y_low,y_high,color,bar_width=0.1):
		v_line = matplotlib.lines.Line2D([x,x],[y_low,y_high],zorder=20,color=color)
		top_h = matplotlib.lines.Line2D([x-bar_width,x+bar_width],[y_high,y_high],zorder=20,color=color)
		bottom_h = matplotlib.lines.Line2D([x-bar_width,x+bar_width],[y_low,y_low],zorder=20,color=color)
		self.ax.add_line(v_line)
		self.ax.add_line(top_h)
		self.ax.add_line(bottom_h)
		
class expression_heat():
	
	def __init__(self,height=19):
		matplotlib.rc('axes',edgecolor='white')

		self.fig=Figure(figsize=(13,((6.0/19)*height)+1))
		self.fig.set_facecolor('white')
		self.ax=self.fig.add_subplot(111)
		self.ax.set_axis_bgcolor('#EEEEEE')
		self.ax.tick_params(axis='both', direction='out')
		self.ax.get_xaxis().tick_bottom()   # remove unneeded ticks 
		self.ax.get_yaxis().tick_left()
		self.x_labels = []
		
		box = self.ax.get_position()
		self.ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
		
		self.data = {}
		
	def add_gene(self,gene):
		
		gene_data = gene.genedata_set.all()
		
		self.data[gene.gene_short_name+' | '+gene.pk] = (map(lambda g:g.fpkm,gene_data))
		self.x_labels = map(lambda f: f.sample_name.sample_name,gene_data)
		
	def response(self,errors=False):
	
		genes = sorted(self.data.keys(),key=lambda n:numpy.mean(self.data[n]),reverse=True)
		
		data_array = []
		
		for g in genes:
			data_array.append(self.data[g])
		data_array = numpy.array(data_array)
		hm = self.ax.imshow(data_array,interpolation='nearest')
		cbar = self.fig.colorbar(hm)
		cbar.ax.set_ylabel('FPKM')
		self.ax.set_yticks(range(len(genes)))
		self.ax.set_yticklabels(genes)
		
		self.ax.set_xticks(range(len(self.x_labels)))
		self.ax.set_xticklabels(self.x_labels,rotation='vertical')
		
		canvas=FigureCanvas(self.fig)
		response=django.http.HttpResponse(content_type='image/png')
		canvas.print_png(response)
		return response