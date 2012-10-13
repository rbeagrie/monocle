# Create your views here.
from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from gene.models import *

@login_required
def index(request):
    datasets = Dataset.objects.all()
    return render_to_response('dataset/index.html',{'datasets':datasets},context_instance=RequestContext(request))

@login_required
def detail(request,dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    return render_to_response('dataset/detail.html',{'dataset':dataset},context_instance=RequestContext(request))
