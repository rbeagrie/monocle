# Create your views here.
from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from gene.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def index(request):
    datasets = Dataset.objects.all()
    return render_to_response('dataset/index.html',{'datasets':datasets},context_instance=RequestContext(request))

@login_required
def detail(request,dataset_id):
    if request.method == 'POST':
        return redirect('dataset.views.compare',sample_1_id=request.POST['sample_1_id'],sample_2_id=request.POST['sample_2_id'])

    dataset = Dataset.objects.get(pk=dataset_id)
    return render_to_response('dataset/detail.html',{'dataset':dataset},context_instance=RequestContext(request))

@login_required
def compare(request,sample_1_id,sample_2_id):

    sample_1 = Sample.objects.get(pk=sample_1_id)
    sample_2 = Sample.objects.get(pk=sample_2_id)

    feature_type = FeatureType.objects.get(name='gene')
        
    data_rows = TestResult.objects.filter(data1__sample=sample_1,data2__sample=sample_2,data1__feature__type=feature_type,data1__value__gt=0.0).order_by('-test_value')[:10]

    data = []

    for row in data_rows:
        point = { 'gene' : row.data1.feature.gene,
                  'value1' : row.data1.value,
                  'value2' : row.data2.value,
                  'change' : row.test_value,
                  'p_value' : row.p_value }
        data.append(point)

    return render_to_response('dataset/compare.html',{'sample_1':sample_1,'sample_2':sample_2,'data':data},context_instance=RequestContext(request))

    
@login_required
def compare_genes(request,sample_1_id,sample_2_id,page=1):
    
    page = int(page)

    sample_1 = Sample.objects.get(pk=sample_1_id)
    sample_2 = Sample.objects.get(pk=sample_2_id)

    feature_type = FeatureType.objects.get(name='gene')
        
    genes = TestResult.objects.filter(data1__sample=sample_1,data2__sample=sample_2,data1__feature__type=feature_type,data1__value__gt=0.0).order_by('-test_value')

    paginator = Paginator(genes, 25) # Show 25 contacts per page

    try:
        data_rows = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        data_rows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        data_rows = paginator.page(paginator.num_pages)

    data = []

    for row in data_rows:
        point = { 'gene' : row.data1.feature.gene,
                  'value1' : row.data1.value,
                  'value2' : row.data2.value,
                  'change' : row.test_value,
                  'p_value' : row.p_value }
        data.append(point)

    all_pages = paginator.page_range
    current_index = all_pages.index(page)
    if current_index == 0:
        first_page = False
        before_pages = []
    else:
        start = current_index - 3
        if start < 0: 
            start = 0
            first_page = False
        else:
            first_page = True

        before_pages = all_pages[start:current_index]

        if before_pages[0] == 1:
            first_page = False

    if current_index == len(all_pages) - 1:
        last_page = False
        after_pages = []
    else:
        start = current_index + 1
        end = current_index + 4
        if end >= len(all_pages) - 1:
            last_page = False
        else:
            last_page = all_pages[-1]

        after_pages = all_pages[start:end]

    pages = {'paginator':data_rows,
             'first_page':first_page,
             'before_pages':before_pages,
             'current_page':page,
             'after_pages':after_pages,
             'last_page':last_page}


    return render_to_response('dataset/compare_genes.html',{'sample_1':sample_1,'sample_2':sample_2,'data':data,'pages':pages},context_instance=RequestContext(request))

