from django.db import models

class Gene(models.Model):
    locus = models.CharField(max_length=45)
    length = models.IntegerField()
    
    def first_name(self):
        name = self.genename_set.all()[0]
        return name.name,name.gene_name_set.name
    
    def __unicode__(self):
        return 'Gene %s (%s)' % self.first_name()
    
    @staticmethod
    def from_tracking_id_and_dataset(tracking_id,dataset):
        namesetname = 'Cufflinks Tracking ID, dataset %i' % dataset.pk
        nameset = GeneNameSet.objects.get(name=namesetname)
        name = GeneName.objects.get(name=tracking_id,gene_name_set=nameset)
        return name.gene

    @staticmethod
    def from_name(name):
        matching_genes = Gene.objects.filter(genename__name__iexact=name).distinct()
        
        # If we didn't find any matching names, return a DoesNotExist error
        if len(matching_genes) == 0 :
            raise Gene.DoesNotExist('The gene %s could not be found in the database.' % name)
        else:
            return matching_genes
    
class GeneNameSet(models.Model):
    name = models.CharField(max_length=70)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name
    
class GeneName(models.Model):
    gene = models.ForeignKey(Gene)
    gene_name_set = models.ForeignKey(GeneNameSet)
    name = models.CharField(max_length=70)

    @staticmethod
    def from_name(name):
        matching_names = GeneName.objects.filter(name__iexact=name)
        
        # If we didn't find any matching names, return a DoesNotExist error
        if len(matching_names) == 0 :
            raise Gene.DoesNotExist('The gene %s could not be found in the database.' % name)
        else:
            return matching_names
    
class Dataset(models.Model):
    name = models.CharField(max_length=70)
    description = models.TextField()
    
class Sample(models.Model):
    dataset = models.ForeignKey(Dataset)
    name = models.CharField(max_length=70)
    description = models.TextField()
    
    def __unicode__(self):
        return 'Sample %s from dataset %i (%s)' % (self.name,self.dataset.pk,self.dataset.name)
    
    @staticmethod
    def from_dataset_and_name(dataset,name):
        return Sample.objects.filter(dataset=dataset).filter(name=name)[0]
    
class FeatureType(models.Model):
    name = models.CharField(max_length=70)
    description = models.TextField()
    
    def __unicode__(self):
        return '%s feature type' % (self.name)
    
class Feature(models.Model):
    gene = models.ForeignKey(Gene)
    type = models.ForeignKey(FeatureType)
    name = models.CharField(max_length=70)
    tracking_id = models.CharField(max_length=45)
    locus = models.CharField(max_length=45)
    length = models.IntegerField()
    
    def __unicode__(self):
        return '%s feature: %s (%s)' % (self.type.name,self.name,self.tracking_id)
    
    @staticmethod
    def from_tracking_id_and_type(tracking_id,type):
        return Feature.objects.filter(tracking_id=tracking_id).filter(type=type)[0]
    
class FeatureData(models.Model):
    feature = models.ForeignKey(Feature)
    sample = models.ForeignKey(Sample)
    value = models.FloatField()
    low_confidence = models.FloatField()
    high_confidence = models.FloatField()
    status = models.CharField(max_length=45)
    
    def __unicode__(self):
        return '%s feature: %s ; Value %f in Sample %s' % (self.feature.type.name,self.feature.name,self.value,self.sample.name)
    
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

    
