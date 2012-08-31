from django.contrib import admin
from gene.models import *

admin.site.register(Gene)
admin.site.register(GeneNameSet)
admin.site.register(GeneName)
admin.site.register(Dataset)
admin.site.register(Sample)
admin.site.register(FeatureType)
admin.site.register(Feature)
admin.site.register(FeatureData)
admin.site.register(TestType)
admin.site.register(TestResult)
admin.site.register(FeatureLink)