# Create your views here.
from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.datastructures import MultiValueDictKeyError
from django.template import RequestContext
from django.core.files.temp import TemporaryFile
from gene.models import *
from list.models import *
from  graphs import *
import numpy
import django

@login_required
def gene(request, gene_id, dataset_id):
    
    gene = get_object_or_404(Gene, pk=gene_id)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    
    graph = expression_line(dataset=dataset)
    graph.add_gene(gene)
        
    graph.ax.set_title(str(gene))
    
    return graph.response(errors=True)    

@login_required    
def tss(request, gene_id, dataset_id):
    
    gene = get_object_or_404(Gene, pk=gene_id)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    tss_groups = get_list_or_404(Feature,gene=gene,type__name='tss_group',featuredata__sample__dataset=dataset)
    
    graph = expression_line(dataset)
    graph.add_tss(gene)
        
    graph.ax.set_title(str(gene))
    
    return graph.response()

@login_required    
def isoform(request, gene_id, dataset_id):
    
    gene = get_object_or_404(Gene, pk=gene_id)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    isoforms = get_list_or_404(Feature,gene=gene,type__name='isoform',featuredata__sample__dataset=dataset)
    
    graph = expression_line(dataset)
    graph.add_isoforms(gene)
        
    graph.ax.set_title(str(gene))
    
    return graph.response()
	
def list(request, list_id, dataset_id):

    list = get_object_or_404(GeneList, pk=list_id)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    samples = Sample.objects.filter(dataset=dataset)
    
    graph = genelist_boxplot()
    
    for sample in samples:
        FPKMS = map( lambda fd : fd.value , FeatureData.objects.filter(sample=sample,feature__type__name='gene',feature__gene__genelist=list))
        print FPKMS
        graph.add_sample(sample.name,FPKMS)
        
    graph.ax.set_title('List #%i - %s' % (list.pk,list.name))
    
    return graph.response()