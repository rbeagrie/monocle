# Create your views here.
from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.datastructures import MultiValueDictKeyError
from django.template import RequestContext
from gene.models import *
from list.models import *
import numpy
import django
import logging

# Get an instance of a logger
logger = logging.getLogger('gene')
print 'level',logger.level

@login_required
def index(request):
    logger.debug('Debug message')
    logger.info('info message')
    print logger
    print 'Happy happy'
    return render_to_response('gene/index.html',{},context_instance=RequestContext(request))

@login_required
def detail(request, gene_id):
    gene = get_object_or_404(Gene, pk=gene_id)
    datasets = Dataset.objects.filter(sample__featuredata__feature__gene=gene).distinct()
    dataset_info = []
    
    for dataset in datasets:
        info = {}
        info['pk'] = dataset.pk
        info['name'] = str(dataset)
        info['tss'] = bool(len(Feature.objects.filter(gene=gene,type__name='tss_group',featuredata__sample__dataset=dataset)))
        info['isoform'] = bool(len(Feature.objects.filter(gene=gene,type__name='isoform',featuredata__sample__dataset=dataset)))
        dataset_info.append(info)
        
        print dataset_info
        
    return render_to_response('gene/detail.html', {'gene' : gene, 'datasets' : dataset_info} ,context_instance=RequestContext(request))

@login_required
def tss(request, gene_id, dataset_id):
    gene = get_object_or_404(Gene, pk=gene_id)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    tss_groups = get_list_or_404(Feature,gene=gene,type__name='tss_group',featuredata__sample__dataset=dataset)
    tss_groups = list(set(tss_groups))
    tss_list = []
    for tss in tss_groups:
        info = {}
        info['name'] = tss.name
        info['isoforms'] = tss.children('tss_link_isoform')
        tss_list.append(info)
    return render_to_response('gene/tss.html', {'gene' : gene, 'dataset' : dataset, 'tss_groups' : tss_list},context_instance=RequestContext(request) )

@login_required
def isoforms(request, gene_id, dataset_id):
    gene = get_object_or_404(Gene, pk=gene_id)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    isoforms = get_list_or_404(Feature,gene=gene,type__name='isoform',featuredata__sample__dataset=dataset)
    isoforms = list(set(isoforms))
    return render_to_response('gene/isoforms.html', {'gene' : gene, 'dataset' : dataset, 'isoforms' : isoforms} ,context_instance=RequestContext(request))
    
@login_required
def similar(request, gene_id, dataset_id):
    g = get_object_or_404(Gene, pk=gene_id)
    d = get_object_or_404(Dataset, pk=dataset_id)
    similar = g.get_similar(d)
    return render_to_response('gene/similar.html', {'gene' : g, 'similar': similar[1:11]} ,context_instance=RequestContext(request))

@login_required
def search(request):
    gene_id=request.GET['gene']
    try:
        names = GeneName.from_name(gene_id)
    except GeneName.DoesNotExist:
        return render_to_response('gene/index.html',{'error_message':'The gene %s does not exist in the database.'%gene_id} ,context_instance=RequestContext(request))
                
    if len(names) == 1:
        gene = names[0].gene
        return redirect(gene)
    
    else:
        return render_to_response('gene/matches.html',{'names':names} ,context_instance=RequestContext(request))

 
