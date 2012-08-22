# Create your views here.
from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.datastructures import MultiValueDictKeyError
from django.template import RequestContext
from django.core.files.temp import TemporaryFile
from gene.models import *
from list.models import *
import numpy
import django

@login_required
def index(request):
    l = GeneList.objects.filter(temp=False)
    return render_to_response('genes/lists.html',{'lists':l},context_instance=RequestContext(request))
    
@login_required    
def upload(request):

    return render_to_response('genes/upload.html',{},context_instance=RequestContext(request))
    
@login_required
def handle(request):
    if request.method == 'POST':
        file_data = request.FILES['list'].read()
        gene_names = map(lambda s:s.strip(),file_data.split('\n'))
        temp_list = GeneList()
        temp_list.name = request.POST['name']
        if temp_list.name != '':
            temp_list.temp = False
        temp_list.save()
        not_found = []
        found_multiple = []
        
        for gene_name in gene_names:
            try:
                matching_genes = Gene.from_name(gene_name)
                if len(matching_genes) == 1:
                    temp_list.genes.add(matching_genes[0])
                else:
                    found_multiple.append(gene_name)
                    
            except Gene.DoesNotExist:
                not_found.append(gene_name)
                
        temp_list.save()
        genes = temp_list.genes.all()
        if len(not_found):
            return render_to_response('genes/handle_list.html',{'gene_list':genes,
                                                                'genes_matched':len(genes),
                                                                'found_multiple':found_multiple,
                                                                'multiple_matched':len(found_multiple),
                                                                'not_found':not_found,
                                                                'not_matched':len(not_found),
                                                                'list_id':temp_list.pk},context_instance=RequestContext(request))
        else:
            return redirect('http://'+request.META['HTTP_HOST']+'/genes/lists/'+str(temp_list.pk))
    else:
        return redirect('http://'+request.META['HTTP_HOST']+'/genes/upload/')
        
@login_required    
def detail(request, list_id):
    
    l = get_object_or_404(GeneList, pk=list_id)
    print l.genes.count()
    
    datasets = Dataset.objects.filter(sample__featuredata__feature__gene__genelist=l).distinct()
    
    if l.genes.count() > 10:
        heat = True
    else:
        heat = False
    
    return render_to_response('genes/list_detail.html',{'list':l,'datasets':datasets},context_instance=RequestContext(request))
