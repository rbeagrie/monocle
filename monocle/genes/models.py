from django.db import models

class Gene(models.Model):
	locus = models.CharField(max_length=45)
	length = models.IntegerField()
	
class GeneNameSet(models.Model):
	name = models.CharField(max_length=70)
	description = models.TextField()
	
class GeneName(models.Model):
	gene = models.ForeignKey(Gene)
	gene_name_set = models.ForeignKey(GeneNameSet)
	name = models.CharField(max_length=70)
	
class Dataset(models.Model):
	name = models.CharField(max_length=70)
	description = models.TextField()
	
class Sample(models.Model):
	dataset = models.ForeignKey(Dataset)
	name = models.CharField(max_length=70)
	description = models.TextField()
	
class FeatureType(models.Model):
	name = models.CharField(max_length=70)
	description = models.TextField()
	
class Feature(models.Model):
	gene = models.ForeignKey(Gene)
	type = models.ForeignKey(FeatureType)
	name = models.CharField(max_length=70)
	tracking_id = models.CharField(max_length=45)
	locus = models.CharField(max_length=45)
	length = models.IntegerField()
	
class FeatureData(models.Model):
	feature = models.ForeignKey(Feature)
	sample = models.ForeignKey(Sample)
	value = models.FloatField()
	low_confidence = models.FloatField()
	high_confidence = models.FloatField()
	status = models.CharField(max_length=45)
	
class TestType(models.Model):
	name = models.CharField(max_length=70)
	description = models.TextField()
	
class TestResult(models.Model):
	feature = models.ForeignKey(Feature)
	type = models.ForeignKey(TestType)
	sample1 = models.ForeignKey(Sample,related_name='+')
	sample2 = models.ForeignKey(Sample,related_name='+')
	test_statistic = models.FloatField()
	status = models.CharField(max_length=45)
	p_value = models.FloatField()
	q_value = models.FloatField()
	
