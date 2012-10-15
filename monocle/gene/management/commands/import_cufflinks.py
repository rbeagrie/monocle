#!/usr/bin/env python

from django.core.management.base import BaseCommand
from gene.models import *
import os, time
from optparse import make_option
from django.db.models import Q

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

LEVELS = {
    0 : 'ERROR',
    1 : 'WARNING',
    2 : 'INFO',
    3 : 'DEBUG'
    }

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
        
        make_option('-t','--tracking_id',
            dest='tracking',
            default=False,
            help='Source of CuffDiff tracking_id identifiers.'),
        )

    def handle(self, *args, **options):
        from django.conf import settings
        from django.utils import translation
        # Activate the current language, because it won't get activated later.
        logger.setLevel(LEVELS[int(options['verbosity'])])
        try:
            translation.activate(settings.LANGUAGE_CODE)
        except AttributeError:
            pass
        import_cufflinks(args,**options)

class CuffDiffImporter(object):
    '''
    CuffDiffImporter is a class that handles importing data from a CuffDiff
    run.
    
    An object of this class must be instantiated with the path to a directory
    containing the output files of a CuffDiff Run.
    '''
    
    def __init__(self,cuffdiff_directory,**options):
        '''
        Initiate the CuffDiffImporter object.
        '''
        
        self.cuffdiff_directory = cuffdiff_directory
        self.options = options
        
    def start_import(self):
        '''
        Start importing data from the specified directory.
        '''
        
        # Add a new dataset
        self.dataset = Dataset()
        self.dataset.save()
        start_time = time.clock()
        print 'Starting Data Import'
        
        # Get the namesets
        
        # Import the genes files
        gene_importer = GeneImporter(self.cuffdiff_directory,self.dataset,**self.options)
        self.gene_index,self.sample_index = gene_importer.get_indexes()
        print gene_importer.output()
        del gene_importer

        
        # Import the TSS files
        feature_importer = FeatureImporter('tss_group',self.cuffdiff_directory,self.dataset,self.gene_index,self.sample_index)
        self.tss_index = feature_importer.feature_index
        print feature_importer.output()
        del feature_importer
        
        # Import the other feature files
        for feature_name in ['isoform','cds']:
            feature_importer = FeatureImporter(feature_name,self.cuffdiff_directory,self.dataset,self.gene_index,self.sample_index,self.tss_index)
            print feature_importer.output()
            del feature_importer
        
        logger.info('Whole import took %f seconds' % time.clock())
        print 'Finished importing data!'

class FeatureImporter(object):
    
    def __init__(self,feature_name,cuffdiff_directory,dataset,gene_index,sample_index=False,tss_index=False,skip_feature=False,**options):
        
        self.cuffdiff_directory = cuffdiff_directory
        self.options = options
        self.dataset = dataset
        self.feature_name = feature_name
        self.gene_index = gene_index
        self.sample_index = sample_index
        self.tss_index = tss_index
        self.skip_feature = skip_feature
        
        # Get the files for this feature
        self.get_files()
        
        # Get the FeatureType object
        self.feature_type,created = FeatureType.objects.get_or_create(name=self.feature_name)
        
        self.process_feature_file()
        
        self.process_tests_file()
        
    def get_files(self):
        
        # Get the name of the file containing feature-level information
        self.feature_file = os.path.join(self.cuffdiff_directory,'%ss.fpkm_tracking' % self.feature_name)
        
        if not os.path.exists(self.feature_file):
            self.feature_file = os.path.join(self.cuffdiff_directory,'%s.fpkm_tracking' % self.feature_name)
        
        # Raise an error if this file does not exist
        assert os.path.exists(self.feature_file)
        
        # Get the name of the file containing feature-level tests
        self.tests_file = os.path.join(self.cuffdiff_directory,'%s_exp.diff' % self.feature_name)
        
        # Raise an error if this file does not exist
        assert os.path.exists(self.tests_file)
        
    def process_feature_file(self):
        
        # Create a new FeatureIndex
        self.feature_index = FeatureIndex(self.feature_type,self.gene_index)
        
        # Create a new Feature Buffer
        self.feature_buffer = Buffer(Feature)
        
        # Create a new FeatureData Buffer
        self.data_buffer = FeatureDataBuffer()
        
        # Create a new TSS link Buffer
        if self.tss_index:
            self.tss_buffer = TssLinkBuffer()
    
        # Open the genes file
        with open(self.feature_file) as features:
        
            # Process the headers
            self.process_headers(features.readline().split())
            
            self.feature_count = 0
            self.data_count = 0
            # Loop over features file
            for line in features:
                self.process_feature_line(line)
                self.feature_count += 1
                if self.feature_count % 1000 == 0:
                    logger.debug('Added %i %ss' % (self.feature_count,self.feature_type.name))
                
        self.save_features()
        
    def process_headers(self,headers):
        self.samples = []
        for i in range(len(self.sample_index)):
            sample_name = headers[9+(i*4)][:-5]
            sample = self.sample_index[sample_name]
            self.samples.append(sample)
    
    def process_feature_line(self,line):
    
        fields = line.split()
        
        tracking_id = fields[0]
        gene_id = fields[3].split(',')[0]
        gene,old = self.gene_index.get(gene_id)
        
        if not tracking_id in self.feature_index:
            if not (self.skip_feature and old):
                
                self.feature_buffer.add(Feature(gene_id=gene,
                                                type=self.feature_type,
                                                name=tracking_id,
                                                tracking_id=tracking_id,
                                                locus=fields[6],
                                                length=0))
                                            
        if self.tss_index and fields[5] != '-':
            tss_ids = fields[5].split(',')
            for tss_id in tss_ids:
                try:
                    tss_group = self.tss_index.get(tss_id)
                except KeyError:
                    logger.warning('Could not find TSS with ID: \'%s\'' % tss_id)
                    continue
                    
                self.tss_buffer.add(tracking_id,FeatureLink(feature2_id=tss_group,name='tss_link_%s'%self.feature_name))
        
        for i,sample in enumerate(self.samples):
            value,low,high,status = fields[9+(i*4):13+(i*4)]
            if low == '-nan':
                low = 0
            if high == '-nan':
                high = 0
            self.data_buffer.add(tracking_id,FeatureData(sample=sample,value=value,low_confidence=low,high_confidence=high,status=status))
            self.data_count += 1
            
    def process_tests_file(self):
    
        # Get the TestType object
        self.test_type,created = TestType.objects.get_or_create(name='expression_t_test')

        # Get a FeatureData index
        self.featuredata_index = FeatureDataIndex(self.dataset,self.feature_type)


        
        # Create a Test Buffer
        self.test_buffer = Buffer(TestResult)
    
        # Open the tests file
        with open(self.tests_file) as tests:
        
            # Skip the headers
            next(tests)
            
            self.test_count = 0
            # Loop over tests file
            for line in tests:
                self.process_tests_line(line)
                self.test_count += 1
                
        self.save_tests()
    
    def process_tests_line(self,line):
    
        fields = line.split()

        data1 = self.featuredata_index.get(fields[0],fields[4])
        data2 = self.featuredata_index.get(fields[0],fields[5])
        
        temp_test = TestResult(
                    type=self.test_type,
                    test_value=fields[9],
                    test_statistic=fields[10],
                    status=fields[6],
                    p_value=fields[11],
                    q_value=fields[12]
                    )

        temp_test.data1_id = data1
        temp_test.data2_id = data2

        self.test_buffer.add(temp_test)
        
    def save_features(self):
        
        self.feature_buffer.process()
        self.feature_index.refresh(self.gene_index)
        self.data_buffer.process(self.feature_index)
        if self.tss_index:
            self.tss_buffer.process(self.feature_index)
        
    def save_tests(self):
        
        self.test_buffer.process()
        
    def output(self):
        
        lines = 'Added %i %ss\n' % (self.feature_count,self.feature_name.capitalize())
        lines += 'Added %i %s Data Points\n' % (self.data_count,self.feature_name.capitalize())
        lines += 'Added %i %s Tests' % (self.test_count,self.feature_name.capitalize())
        return lines
        
class GeneImporter(FeatureImporter):
    def __init__(self,cuffdiff_directory,dataset,**options):
        
        # Get or create the NameSets
        self.ns_parser = NameSetParser(dataset,**options)
        
        self.gene_count = 0
        self.name_count = 0
    
        # Initiate the parent class with 'gene' as the feature type
        FeatureImporter.__init__(self,'gene',cuffdiff_directory,dataset,GeneIndex(),skip_feature=True,**options)
        
    def process_headers(self,headers):
        # Get sample names from the column headers
        self.get_samples(headers)
        FeatureImporter.process_headers(self,headers)
          
    def get_samples(self,headers):
    
        # Determine the number of samples
        no_samples = (len(headers) - 9)/4
        self.sample_index = {}
        
        # Add samples
        for i in range(no_samples):
            field_no = (i*4)+9
            sample_name = headers[field_no][:-5]
            new_sample = Sample(name=sample_name,dataset=self.dataset)
            new_sample.save()
            self.sample_index[new_sample.name] = new_sample
            
            self.sample_count = len(self.sample_index)
        
    def process_feature_line(self,line):
    
        fields = line.split()
                
        # Parse and add gene names
        gene,old = self.ns_parser.parse(fields)
        
        # Add the gene to the index
        self.gene_index.add(gene,fields[0],old)
        
        FeatureImporter.process_feature_line(self,line)
        
    def save_features(self):
        
        self.ns_parser.save()
        
        FeatureImporter.save_features(self)
        
    def get_indexes(self):
        
        return self.gene_index,self.sample_index
        
    def output(self):
        lines = 'Added %i Samples\n' % self.sample_count
        lines += 'Added %i Name Sets\n' % self.ns_parser.nameset_count
        lines += 'Added %i Names\n' % self.ns_parser.name_count
        lines += FeatureImporter.output(self)
        return lines
        
class FeatureIndex(object):
    def __init__(self,feature_type,gene_index):
        
        self.features = {}
        self.feature_type = feature_type
        self.refresh(gene_index)
        
    def refresh(self,gene_index):
        
        del self.features
        self.features = {}
        ids = gene_index.get_ids()
        feature_list = Feature.objects.filter(gene__id__in = ids, type=self.feature_type).values('tracking_id','id')
        for feature in feature_list:
                
            self.features[feature['tracking_id']] = feature['id']
        
        del feature_list
       
    def __contains__(self,tracking_id):
        return tracking_id in self.features
        
    def get(self,tracking_id):
        return self.features[tracking_id]
    
class FeatureDataIndex(object):
    def __init__(self,dataset,feature_type):
        self.data = {}
        featuredatas = FeatureData.objects.filter(feature__type=feature_type,sample__dataset=dataset).select_related('feature').select_related('sample')
        for featuredata in featuredatas:
            self.add(featuredata.feature.tracking_id,featuredata.sample.name,featuredata.pk)
        del featuredatas

    def add(self,feature_tracking_id,sample_name,data_id):
        if feature_tracking_id not in self.data:
            self.data[feature_tracking_id] = {}
        self.data[feature_tracking_id][sample_name] = data_id

    def get(self,feature_tracking_id,sample_name):
        return self.data[feature_tracking_id][sample_name]

class GeneIndex(object):
    def __init__(self):
    
        self.genes = {}
        self.gene_ids = {}
        
    def add(self,gene,tracking_id,old):
    
        self.genes[tracking_id] = gene.id,old
        self.gene_ids[gene.pk] = tracking_id
        
    def get_ids(self):
        
        return self.gene_ids.keys()
        
    def tracking_from_pk(self,pk):
        
        return self.gene_ids[pk]
        
    def get(self,tracking_id):
        
        return self.genes[tracking_id]
    
class GeneNameIndex(object):
    def __init__(self,nameset,field):
        
        self.index = {}
        self.field = field
        self.nameset = nameset
        names = GeneName.objects.filter(gene_name_set=nameset).values('name','gene_id')
        for name in names:
            self.index[name['name']] = name['gene_id']

        del names
            
    def get_name(self,fields):
        
        name = fields[self.field]
        if name != '-':
            return name
        else:
            return False
        
    def parse(self,fields):
        
        name = self.get_name(fields)
        if name:
            try:
                return self.index[name]
            except KeyError:
                return False
        else:
            return False
        
class NameSetParser(object):

    def __init__(self,dataset,short_name=False,cuff_id=False,nearest_ref=False,tracking=False,**options):
    
        self.old_namesets = []
        self.new_namesets = []
        
        self.incomplete_names = []
        
        self.gene_count = 0
        self.name_count = 0
        
        self.all_namesets = set()
        
        self.start_time = time.clock()
        
        self.name_buffer = Buffer(GeneName)
            
        if not short_name:
            short_name = 'Cufflinks Short Name, dataset %i' % dataset.pk
            
        self.add_nameset(short_name, 4)
            
        if not cuff_id:
            cuff_id = 'Cufflinks Gene ID, dataset %i' % dataset.pk
            
        if cuff_id not in self.all_namesets:    
            self.add_nameset(cuff_id, 3)
        
        if not tracking:        
            tracking = 'Cufflinks Tracking ID, dataset %i' % dataset.pk
            
        if tracking not in self.all_namesets:    
            self.add_nameset(tracking,0)
        
        if not nearest_ref:
            nearest_ref = 'Cufflinks nearest_ref, dataset %i' % dataset.pk
            
        if nearest_ref not in self.all_namesets:    
            self.add_nameset(nearest_ref,2)
            
        self.nameset_count = len(self.new_namesets)
            
    def add_nameset(self,name,field):
        self.all_namesets.add(name)
        ns,created = GeneNameSet.objects.get_or_create(name=name)
        ns.save()
    
        if created:
            self.new_namesets.append( (ns,field) )
        else:
            index = GeneNameIndex(ns,field)
            self.old_namesets.append( index )
            
    def add_gene(self,gene):
        
        for new_name in self.incomplete_names:
            new_name.gene = gene
            self.name_buffer.add(new_name)
            self.name_count += 1
            
        self.incomplete_names = []
        
    def parse(self,fields):
        
        old_names = []
        query_chain = Q()
        gene = False
        old = True
        
        for index in self.old_namesets:
            # This is an ugly hack, skip the short name as it may be duplicated.
            if index.field == 4:
                continue
            gene = index.parse(fields)
            if gene:
                break
            
        if not gene:
            for index in self.old_namesets:
                name = index.get_name(fields)
                ns = index.nameset
                self.incomplete_names.append(GeneName(gene_name_set=ns,name=name))
                      
        for ns,field in self.new_namesets:
            if fields[field] == '-':
                continue
                
            self.incomplete_names.append(GeneName(gene_name_set=ns,name=fields[field]))
        
        # Make a new gene if none was found
        if not gene:
            gene = Gene(locus=fields[6],length=0)
            gene.save()
            old = False
            
        self.gene_count += 1
            
        self.add_gene(gene)
        
        return gene,old
            
    def save(self):
        
        self.name_buffer.process()
        
class Buffer(object):
    def __init__(self,model_class):
        
        self.model = model_class
        self.batch_size = 900 / len(model_class._meta.fields)
        self.objects = []
        self.start_time = time.clock()
        
    def add(self,object):
    
        self.objects.append(object)
        if len(self.objects) > 2 * self.batch_size:
            self.process()
        
    def process(self):
        unprocessed = []
        for obj in self.objects:
            unprocessed.append(obj)
            if len(unprocessed) % self.batch_size == 0:
                self.model.objects.bulk_create(unprocessed)
                unprocessed = []
                
        self.model.objects.bulk_create(unprocessed)
                
        logger.info('Added %i %ss in %f seconds.' % (len(self.objects),self.model.__name__,time.clock()-self.start_time))
        del self.objects
        self.objects = []
            
class FeatureDataBuffer(Buffer):
    def __init__(self):
        Buffer.__init__(self,FeatureData)
        self.data_store = {}
        self.count = 0
        
    def add(self,tracking_id,data):
        
        if tracking_id not in self.data_store:
            self.data_store[tracking_id] = []
        
        self.data_store[tracking_id].append(data)
        self.count += 1

        if self.count >= self.batch_size:
            self.process()
        self.count = 0
        
    def process(self,feature_index):
        for tracking_id in self.data_store:
            feature = feature_index.get(tracking_id)
            for data_point in self.data_store[tracking_id]:
                data_point.feature_id = feature
                self.objects.append(data_point)
        Buffer.process(self)
        del self.data_store
        self.data_store = {}
            
class TssLinkBuffer(FeatureDataBuffer):
    def __init__(self):
        Buffer.__init__(self,FeatureLink)
        self.data_store = {}
        
    def process(self,feature_index):
        for tracking_id in self.data_store:
            feature = feature_index.get(tracking_id)
            for data_point in self.data_store[tracking_id]:
                data_point.feature1_id = feature
                self.objects.append(data_point)
        Buffer.process(self)
        del self.data_store
        self.data_store = {}

def import_cufflinks(argset=[], **kwargs):
    cuffdir = argset[0]
    assert os.path.isdir(cuffdir)
    
    importer = CuffDiffImporter(cuffdir,**kwargs)
    importer.start_import()


if __name__ == '__main__':
    runcpserver(sys.argv[1:])
