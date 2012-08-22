from django.db import models
from gene.models import Gene
				
class GeneList(models.Model):
	name = models.CharField(max_length=45)
	temp = models.BooleanField(default=True)
	genes = models.ManyToManyField(Gene)