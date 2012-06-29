#!/usr/bin/env python

from django.core.management.base import BaseCommand
from genes.models import *
import os

class Command(BaseCommand):
	args = "[various KEY=val options, use `runcpserver help` for help]"
	
	IMPORTER_HELP = r"""
  Run this project in a CherryPy webserver. To do this, CherryPy from
  http://www.cherrypy.org/ is required.

   runcpserver [options] [cpserver settings] [stop]

Optional CherryPy server settings: (setting=value)
  host=HOSTNAME         hostname to listen on
                        Defaults to localhost
  port=PORTNUM          port to listen on
                        Defaults to 8088
  server_name=STRING    CherryPy's SERVER_NAME environ entry
                        Defaults to localhost
  daemonize=BOOL        whether to detach from terminal
                        Defaults to False
  pidfile=FILE          write the spawned process-id to this file
  workdir=DIRECTORY     change to this directory when daemonizing
  threads=NUMBER        Number of threads for server to use
  ssl_certificate=FILE  SSL certificate file
  ssl_private_key=FILE  SSL private key file
  server_user=STRING    user to run daemonized process
                        Defaults to www-data
  server_group=STRING   group to daemonized process
                        Defaults to www-data

Examples:
  Run a "standard" CherryPy server server
    $ manage.py runcpserver

  Run a CherryPy server on port 80
    $ manage.py runcpserver port=80

  Run a CherryPy server as a daemon and write the spawned PID in a file
    $ manage.py runcpserver daemonize=true pidfile=/var/run/django-cpserver.pid

"""

	def handle(self, *args, **options):
		from django.conf import settings
		from django.utils import translation
		# Activate the current language, because it won't get activated later.
		try:
			translation.activate(settings.LANGUAGE_CODE)
		except AttributeError:
			pass
		import_cufflinks(args)
		
	def usage(self, subcommand):
		return ' '

def process_genes_file(genes_fpkms,dataset):
	
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
	
	whole_gene,created = FeatureType.objects.get_or_create(name='whole_gene')
	
	tracking_nameset = GeneNameSet(name='Cufflinks Tracking, dataset %i' % dataset.pk)
	tracking_nameset.save()
	
	short_nameset = GeneNameSet(name='Cufflinks Short Name, dataset %i' % dataset.pk)
	short_nameset.save()
	
	gene_id_nameset = GeneNameSet(name='Cufflinks Gene Id, dataset %i' % dataset.pk)
	gene_id_nameset.save()
	
	for line in genes_file:
		fields = line.split()
		gene = Gene(locus=fields[6],length=0)
		gene.save()
		
		short_name = GeneName(gene=gene,gene_name_set=short_nameset,name=fields[4])
		short_name.save()
		
		GeneName(gene=gene,gene_name_set=tracking_nameset,name=fields[0]).save()
		
		GeneName(gene=gene,gene_name_set=gene_id_nameset,name=fields[3]).save()
		
		feature = Feature(gene=gene,type=whole_gene,name=fields[4],tracking_id=fields[0],locus=fields[6],length=0)
		feature.save()
		
		for i,sample in enumerate(samples):
			
			value,low,high,status = fields[9+(i*4):13+(i*4)]
			FeatureData(feature=feature,sample=sample,value=value,low_confidence=low,high_confidence=high,status=status).save()
			
def process_tests_file(tests_file,dataset,feature,test):
	feature_type,created = FeatureType.objects.get_or_create(name=feature)
	test_type,created = TestType.objects.get_or_create(name=test)
	with open(tests_file) as tests:
		next(tests)
		for line in tests:
			fields = line.split()
			feature = Feature.from_tracking_id_and_type(fields[1],feature_type)
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
						
def process_feature_file(filename,dataset,feature):
	
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
	
	for line in feature_file:
		fields = line.split()
		gene = Gene.from_tracking_id_and_dataset(fields[3],dataset)
		print gene
		'''		
		short_name = GeneName(gene=gene,gene_name_set=short_nameset,name=fields[4])
		short_name.save()
		
		GeneName(gene=gene,gene_name_set=tracking_nameset,name=fields[0]).save()
		
		GeneName(gene=gene,gene_name_set=gene_id_nameset,name=fields[3]).save()
		
		feature = Feature(gene=gene,type=whole_gene,name=fields[4],tracking_id=fields[0],locus=fields[6],length=0)
		feature.save()
		
		for i,sample in enumerate(samples):
			
			value,low,high,status = fields[9+(i*4):13+(i*4)]
			FeatureData(feature=feature,sample=sample,value=value,low_confidence=low,high_confidence=high,status=status).save()'''
		
def process_cufflinks_directory(cuffdir):
	
	genes_fpkm_file = os.path.join(cuffdir,'genes.fpkm_tracking')
	assert os.path.exists(genes_fpkm_file)
	
	dataset = Dataset()
	dataset.save()
	
	process_genes_file(genes_fpkm_file,dataset)
	
	genes_tests_file = os.path.join(cuffdir,'gene_exp.diff')
	assert os.path.exists(genes_tests_file)
	
	process_tests_file(genes_tests_file,dataset,'whole_gene','expression_t_test')
	
	isoforms_file = os.path.join(cuffdir,'isoforms.fpkm_tracking')
	assert os.path.exists(isoforms_file)
	
	process_feature_file(isoforms_file,dataset,'isoform')

def import_cufflinks(argset=[], **kwargs):
	
	cuffdir = argset[0]
	print cuffdir
	assert os.path.isdir(cuffdir)
	
	process_cufflinks_directory(cuffdir)
	
	if "help" in argset:
		print ' '
		return


if __name__ == '__main__':
	runcpserver(sys.argv[1:])
