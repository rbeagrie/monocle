#!/usr/bin/env python

from django.core.management.base import BaseCommand
from gene.models import *
import os, time
from optparse import make_option

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = "[cuffdiff_directory]"
    help = "Imports data from a CuffDiff run"
    
    option_list = BaseCommand.option_list + (
        make_option('-n','--nearest_ref',
            dest='nearest_ref',
            default=False,
            help='Source of CuffDiff nearest_ref identifiers.'),
        
        make_option('-i','--id',
            dest='cuff_id',
            default=False,
            help='Source of CuffDiff gene_id identifiers.'),
        
        make_option('-s','--short_name',
            dest='short_name',
            default=False,
            help='Source of CuffDiff short_name identifiers.'),
        )

    def handle(self, *args, **options):
        from django.conf import settings
        from django.utils import translation
        # Activate the current language, because it won't get activated later.
        try:
            translation.activate(settings.LANGUAGE_CODE)
        except AttributeError:
            pass
        import_cufflinks(args,**options)

def process_genes_file(genes_fpkms,dataset,nearest_ref=False,cuff_id=False,short_name=False,**kwargs):

    genes_file = open(genes_fpkms)
    first_line = genes_file.readline()
    headers = first_line.split()
    no_samples = (len(headers) - 9)/4
    samples = []
    for i in range(no_samples):
        field_no = (i*4)+9
        sample_name = headers[field_no][:-5]
        new_sample = Sample(name=sample_name,dataset=dataset)
        new_sample.save()
        samples.append(new_sample)
        
    print 'Added %i Samples' % len(samples)
    
    whole_gene,created = FeatureType.objects.get_or_create(name='whole_gene')
    
    old_namesets = []
    new_namesets = []
    
    def add_nameset(name,field):
        ns,created = GeneNameSet.objects.get_or_create(name=name)
        ns.save()
    
        if created:
            new_namesets.append( (ns,field) )
        else:
            old_namesets.append( (ns,field) )
        
    if not short_name:
        short_name = 'Cufflinks Short Name, dataset %i' % dataset.pk
        
    add_nameset(short_name, 4)
        
    if not cuff_id:
        cuff_id = 'Cufflinks Gene ID, dataset %i' % dataset.pk
        
    add_nameset(cuff_id, 3)
    
    if not nearest_ref:
        nearest_ref = 'Cufflinks nearest_ref, dataset %i' % dataset.pk
    add_nameset(nearest_ref,2)
        
    tracking = 'Cufflinks Tracking ID, dataset %i' % dataset.pk
        
    add_nameset(tracking,0)
    
    print 'Added %i Gene Name Sets' % len(new_namesets)
    
    gene_count = 0
    name_count = 0
    
    start_time = time.clock()
    unsaved_features = []
    unsaved_data = {}
    for line in genes_file:
        fields = line.split()
        
        gene = False
        names = []
        
        for ns,field in old_namesets:
            if fields[field] == '-':

                continue
            
            if not gene:
            
                try:
                    name = GeneName.objects.get(gene_name_set=ns,name=fields[field])
                    gene = name.gene
                    
                except (GeneName.DoesNotExist, GeneName.MultipleObjectsReturned):
                    name = GeneName(gene_name_set=ns,name=fields[field])
            
            else:
                try:
                    name = GeneName.objects.get(gene=gene,gene_name_set=ns,name=fields[field])
                    
                except GeneName.DoesNotExist:
                    name = GeneName(gene=gene,gene_name_set=ns,name=fields[field])
                
            names.append(name)
            
        for ns,field in new_namesets:
            if fields[field] == '-':
                continue
            
            if not gene:
                name = GeneName(gene_name_set=ns,name=fields[field])
            else:
                name = GeneName(gene=gene,gene_name_set=ns,name=fields[field])
                
            names.append(name)
                
        if not gene:
            gene = Gene(locus=fields[6],length=0)
            gene_count += 1
            gene.save()

            
        for name in names:
            name.gene = gene
            if GeneName.objects.filter(gene = name.gene, gene_name_set = name.gene_name_set, name = name.name).count():
                continue
            name_count += 1
            name.save()
        
        try:
            Feature.objects.get(gene=gene,type=whole_gene,name=fields[4],tracking_id=fields[0],locus=fields[6],length=0)
        except:
            unsaved_features.append(Feature(gene=gene,type=whole_gene,name=fields[4],tracking_id=fields[0],locus=fields[6],length=0))

        unsaved_data[fields[0]] = []
        for i,sample in enumerate(samples):
            
            value,low,high,status = fields[9+(i*4):13+(i*4)]
            unsaved_data[fields[0]].append(FeatureData(sample=sample,value=value,low_confidence=low,high_confidence=high,status=status))
        
        #logger.debug('Added Gene %i: %s' % (gene_count,feature.name))
        if gene_count % 1000 == 0:
            Feature.objects.bulk_create(unsaved_features)
            unsaved_features = []
            total_time = time.clock() - start_time
            logger.info('Added %i genes in %f seconds.' % (gene_count,total_time))
    print 'Added %i Genes' % gene_count
    print 'Added %i Gene Names' % name_count
            
def process_tests_file(tests_file,dataset,feature,test):
    feature_type,created = FeatureType.objects.get_or_create(name=feature)
    test_type,created = TestType.objects.get_or_create(name=test)
    test_count = 0
    with open(tests_file) as tests:
        next(tests)
        for line in tests:
            test_count += 1
            fields = line.split()
   
            
            feature = Feature.from_tracking_id_and_type(fields[0],feature_type)
            sample1 = Sample.from_dataset_and_name(dataset,fields[4])
            sample2 = Sample.from_dataset_and_name(dataset,fields[5])
            TestResult(feature=feature,
                        type=test_type,
                        sample1=sample1,
                        sample2=sample2,
                        test_statistic=fields[10],
                        status=fields[6],
                        p_value=fields[11],
                        q_value=fields[12]
                        ).save()
                        
    print 'Added %i Tests (%s - %s)' % (test_count,feature_type.name,test_type.name)
                        
def process_feature_file(filename,dataset,feature):
    feature_count = 0
    feature_file = open(filename)
    first_line = feature_file.readline()
    headers = first_line.split()
    no_samples = (len(headers) - 9)/4
    samples = []
    for i in range(no_samples):
        field_no = (i*4)+9
        sample_name = headers[field_no][:-5]
        samples.append(Sample.from_dataset_and_name(dataset,sample_name))
    
    feature_type,created = FeatureType.objects.get_or_create(name=feature)
    tss_type = FeatureType.objects.get(name='tss_group')
    
    for line in feature_file:
        fields = line.split()
        feature_count += 1
        gene = Gene.from_tracking_id_and_dataset(fields[3],dataset)
        
        feature,created = Feature.objects.get_or_create(gene=gene,type=feature_type,name=fields[0],tracking_id=fields[0],locus=fields[6],length=0)
        feature.save()
        
        if feature_type.name != 'tss_group' and fields[5] != '-':
            tss_id = fields[5]
            tss_group = Feature.from_tracking_id_and_type(tss_id,tss_type)
            tss_link = FeatureLink(feature1=feature,feature2=tss_group,name='tss_link_%s'%feature_type.name)
            tss_link.save()
              
        for i,sample in enumerate(samples):
            
            value,low,high,status = fields[9+(i*4):13+(i*4)]
            feature_data = FeatureData(feature=feature,sample=sample,value=float(value),low_confidence=low,high_confidence=high,status=status)
            feature_data.save()
            
    print 'Added %i %ss' % (feature_count,feature_type.name)
        
def process_cufflinks_directory(cuffdir,**kwargs):
    
    genes_fpkm_file = os.path.join(cuffdir,'genes.fpkm_tracking')
    assert os.path.exists(genes_fpkm_file)
    
    dataset = Dataset()
    dataset.save()
    
    process_genes_file(genes_fpkm_file,dataset,**kwargs)
    
    genes_tests_file = os.path.join(cuffdir,'gene_exp.diff')
    assert os.path.exists(genes_tests_file)
    
    process_tests_file(genes_tests_file,dataset,'whole_gene','expression_t_test')
    
    # Process the tss_groups.fpkm_tracking file
    TSS_file = os.path.join(cuffdir,'tss_groups.fpkm_tracking')
    assert os.path.exists(TSS_file)
    
    process_feature_file(TSS_file,dataset,'tss_group')
    
    # Process the tss_group_exp.diff file
    TSS_tests_file = os.path.join(cuffdir,'tss_group_exp.diff')
    assert os.path.exists(TSS_tests_file)
    
    process_tests_file(TSS_tests_file,dataset,'tss_group','expression_t_test')
    
    # Process the isoforms.fpkm_tracking file
    isoforms_file = os.path.join(cuffdir,'isoforms.fpkm_tracking')
    assert os.path.exists(isoforms_file)
    
    process_feature_file(isoforms_file,dataset,'isoform')
    
    # Process the isoform_exp.diff file
    isoform_tests_file = os.path.join(cuffdir,'isoform_exp.diff')
    assert os.path.exists(isoform_tests_file)
    
    process_tests_file(isoform_tests_file,dataset,'isoform','expression_t_test')

def import_cufflinks(argset=[], **kwargs):
    cuffdir = argset[0]
    assert os.path.isdir(cuffdir)
    
    process_cufflinks_directory(cuffdir,**kwargs)


if __name__ == '__main__':
    runcpserver(sys.argv[1:])
