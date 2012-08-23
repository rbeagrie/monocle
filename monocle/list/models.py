from django.db import models
from gene.models import Gene
                
class GeneList(models.Model):
    name = models.CharField(max_length=45)
    temp = models.BooleanField(default=True)
    genes = models.ManyToManyField(Gene)
        
    def get_absolute_url(self):
        return "/list/%i/" % self.pk
        
    def __unicode__(self):
        return self.name