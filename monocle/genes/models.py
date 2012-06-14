from django.db import models
import numpy as np

# Create your models here.

class Gene(models.Model):
	class Meta:
		db_table = 'genes'
	gene_id = models.CharField(max_length=45,primary_key=True)
	gene_short_name = models.CharField(max_length=45)
	locus = models.CharField(max_length=45)

	def p_dist(self):
                fpkms = map(lambda f: f.fpkm,self.genedata_set.all())
                for i in range(len(fpkms)):
                        if fpkms[i] == 0.0:
                                fpkms[i] = 10**(-13)
                total = sum(fpkms)
                return np.array(map(lambda f: f/total,fpkms))
						
	def jsd(self,gene):
                P = self.p_dist()
                Q = gene.p_dist()
                
                M = (P+Q)/2
                
                def kld(P,Q):
                        total = 0.0
                        for i,p in enumerate(P):
                                total += (P[i]*np.log(P[i]/Q[i]))
                        return total

                return kld(P,M)/2 + kld(P,M)/2

        def get_similar(self):

                genes = list(Gene.objects.all())
                
                return sorted(genes, key = lambda g : g.jsd(self) )

        def max_fpkm(self):
                return max(map(lambda f: f.fpkm,self.genedata_set.all()))
	
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

class Sample(models.Model):
	class Meta:
		db_table = 'samples'
	sample_name = models.CharField(max_length=45,primary_key=True,db_column='sample_name')

class GeneData(models.Model):
        class Meta:
                db_table = 'geneData'
        gene = models.ForeignKey(Gene)
        sample_name = models.ForeignKey(Sample,db_column='sample_name')
        fpkm = models.FloatField(primary_key=True)
        conf_hi = models.FloatField()
        conf_lo = models.FloatField()
        quant_status = models.CharField(max_length=45)

class TssData(models.Model):
        class Meta:
                db_table = 'TSSData'
        TSS_group = models.ForeignKey(Tss)
        sample_name = models.ForeignKey(Sample,db_column='sample_name')
        fpkm = models.FloatField(primary_key=True)
        conf_hi = models.FloatField()
        conf_lo = models.FloatField()
        quant_status = models.CharField(max_length=45)

class IsoformData(models.Model):
        class Meta:
                db_table = 'isoformData'
        isoform = models.ForeignKey(Isoform)
        sample_name = models.ForeignKey(Sample,db_column='sample_name')
        fpkm = models.FloatField(primary_key=True)
        conf_hi = models.FloatField()
        conf_lo = models.FloatField()
        quant_status = models.CharField(max_length=45)
