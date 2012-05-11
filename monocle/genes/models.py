from django.db import models

# Create your models here.

class Gene(models.Model):
	class Meta:
		db_table = 'genes'
	gene_id = models.CharField(max_length=45,primary_key=True)
	gene_short_name = models.CharField(max_length=45)
	locus = models.CharField(max_length=45)
	
class Tss(models.Model):
	class Meta:
		db_table = 'TSS'
	TSS_group_id = models.CharField(max_length=45,primary_key=True)
	gene = models.ForeignKey(Gene)
	locus = models.CharField(max_length=45)
	
class Isoform(models.Model):
	class Meta:
		db_table = 'isoforms'
	isoform_id = models.CharField(max_length=45,primary_key=True)
	gene = models.ForeignKey(Gene)
	TSS_group = models.ForeignKey(Tss)
	nearest_ref_id = models.CharField(max_length=45)