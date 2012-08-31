from gene.models import *
from list.models import *

import django

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import matplotlib, pylab

class expression_line():
    
    def __init__(self,dataset):
        matplotlib.rc('axes',edgecolor='white')

        self.dataset = dataset
        self.fig=Figure(figsize=(13,6))
        self.fig.set_facecolor('white')
        self.ax=self.fig.add_subplot(111)
        self.ax.set_axis_bgcolor('#EEEEEE')
        self.ax.grid(True,color='white',ls='-',lw=2,zorder=2)
        self.ax.tick_params(axis='both', direction='out')
        self.ax.get_xaxis().tick_bottom()   # remove unneeded ticks 
        self.ax.get_yaxis().tick_left()
        self.legend_entries = {}
        self.y_lows = []
        self.y_highs = []
        self.errors = []
        
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])

        
        self.y_low = 'unset'
        self.y_high = 'unset'
        
        self.colors = ['#1F78B4','#33A02C','#E31A1C','#FF7F00','#6A3D9A','#A6CEE3','#B2DF8A','#FB9A99','#FDBF6F','#CAB2D6','#FFFF99']
        self.color_index = 0
        
    def next_color(self):
        col = self.colors[self.color_index % len(self.colors)]
        self.color_index += 1
        return col
        
    def add_gene(self,gene):
        
        feature_type = FeatureType.objects.get(name='gene')
        feature = Feature.objects.get(gene=gene,type=feature_type)
        gene_data = FeatureData.objects.filter(feature=feature,sample__dataset=self.dataset)
        
        gene_line = self.add_data(gene_data)
        self.legend_entries[str(gene)] = gene_line
        
        for i,gd in enumerate(gene_data):
        
            self.errors.append((i,gd.low_confidence,gd.high_confidence,gene_line.get_color()))
        
    def response(self,errors=False):
        self.ax.set_xticks(range(len(self.x_labels)))
        self.ax.set_xticklabels(self.x_labels,rotation='vertical')
        self.ax.set_ylabel('FPKM')
        
        self.ax.legend(self.legend_entries.values(),self.legend_entries.keys(),loc='center left', bbox_to_anchor=(1, 0.5))
        
        if errors:
            for i in range(len(self.errors)):
                self.draw_error(*self.errors[i])
            y_low = min(self.y_lows)
            y_high = max(self.y_highs)
            
            self.update_y_limits(y_low,y_high)
        canvas=FigureCanvas(self.fig)
        response=django.http.HttpResponse(content_type='image/png')
        canvas.print_png(response)
        return response
        
    def add_tss(self,gene):
        feature_type = FeatureType.objects.get(name='tss_group')
        features = Feature.objects.filter(gene=gene,type=feature_type)
        for feature in features:
            gene_data = FeatureData.objects.filter(feature=feature,sample__dataset=self.dataset)
            line = self.add_data(gene_data)
            self.legend_entries[feature.tracking_id] = line
        
    def add_isoforms(self,gene):
        
        isoforms = Feature.objects.filter(gene=gene,type__name='isoform')
        
        for feature in isoforms:
            gene_data = FeatureData.objects.filter(feature=feature,sample__dataset=self.dataset)
            print 'data',gene_data
            line = self.add_data(gene_data)
            self.legend_entries[feature.name] = line
        
        
    def add_data(self,gene_data):
    
        self.x_labels = map(lambda f: f.sample.name,gene_data)
        print 'test',map(lambda f: f.sample.name,gene_data)
        self.y_lows.extend(map(lambda f: f.low_confidence,gene_data))
        self.y_highs.extend(map(lambda f: f.high_confidence,gene_data))

        fpkms = map(lambda f: f.value,gene_data)
        x=range(len(fpkms))
        y=fpkms
        gene_line = self.ax.plot(x,y,zorder=10,label='Gene',color=self.next_color())
        
        self.ax.set_xlim(-0.5,len(fpkms)-0.5)
        
        y_low = min(fpkms)
        y_high = max(fpkms)
        
        self.update_y_limits(y_low,y_high)
        
        return gene_line[0]
        
    def update_y_limits(self,new_low,new_high):
        if self.y_low == 'unset':
            self.y_low = new_low
        elif self.y_low > new_low:
            self.y_low = new_low
        
        if self.y_high == 'unset':
            self.y_high = new_high
        elif self.y_high < new_high:
            self.y_high = new_high
        
        self.ax.set_ylim(self.y_low-0.5,self.y_high+0.5)
    
    def draw_error(self,x,y_low,y_high,color,bar_width=0.1):
        v_line = matplotlib.lines.Line2D([x,x],[y_low,y_high],zorder=20,color=color)
        top_h = matplotlib.lines.Line2D([x-bar_width,x+bar_width],[y_high,y_high],zorder=20,color=color)
        bottom_h = matplotlib.lines.Line2D([x-bar_width,x+bar_width],[y_low,y_low],zorder=20,color=color)
        self.ax.add_line(v_line)
        self.ax.add_line(top_h)
        self.ax.add_line(bottom_h)
        
class expression_heat():
    
    def __init__(self,height=19):
        matplotlib.rc('axes',edgecolor='white')

        self.fig=Figure(figsize=(13,((6.0/19)*height)+1))
        self.fig.set_facecolor('white')
        self.ax=self.fig.add_subplot(111)
        self.ax.set_axis_bgcolor('#EEEEEE')
        self.ax.tick_params(axis='both', direction='out')
        self.ax.get_xaxis().tick_bottom()   # remove unneeded ticks 
        self.ax.get_yaxis().tick_left()
        self.x_labels = []
        
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
        
        self.data = {}
        
    def add_gene(self,gene):
        
        gene_data = gene.genedata_set.all()
        
        self.data[gene.gene_short_name+' | '+gene.pk] = (map(lambda g:g.fpkm,gene_data))
        self.x_labels = map(lambda f: f.sample_name.sample_name,gene_data)
        
    def response(self,errors=False):
    
        genes = sorted(self.data.keys(),key=lambda n:numpy.mean(self.data[n]),reverse=True)
        
        data_array = []
        
        for g in genes:
            data_array.append(self.data[g])
        data_array = numpy.array(data_array)
        hm = self.ax.imshow(data_array,interpolation='nearest')
        cbar = self.fig.colorbar(hm)
        cbar.ax.set_ylabel('FPKM')
        self.ax.set_yticks(range(len(genes)))
        self.ax.set_yticklabels(genes)
        
        self.ax.set_xticks(range(len(self.x_labels)))
        self.ax.set_xticklabels(self.x_labels,rotation='vertical')
        
        canvas=FigureCanvas(self.fig)
        response=django.http.HttpResponse(content_type='image/png')
        canvas.print_png(response)
        return response
        
class genelist_boxplot():
    
    def __init__(self,height=19):
        matplotlib.rc('axes',edgecolor='white')

        self.fig=Figure(figsize=(13,((6.0/19)*height)+1))
        self.fig.set_facecolor('white')
        self.ax=self.fig.add_subplot(111)
        self.ax.set_axis_bgcolor('#EEEEEE')
        self.ax.tick_params(axis='both', direction='out')
        self.ax.get_xaxis().tick_bottom()   # remove unneeded ticks 
        self.ax.get_yaxis().tick_left()
        self.ax.set_yscale('log')
        self.x_labels = []
        self.list_data = []
        
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
        
    def add_sample(self,name,fpkms):
        self.list_data.append(fpkms)
        self.x_labels.append(name)
        
    def response(self,errors=False):
        bp = self.ax.boxplot(self.list_data,
        widths = 0.8,patch_artist=True,sym='wo')
        pylab.setp(bp['boxes'],facecolor='#D9D9D9')
        pylab.setp(bp['whiskers'],color='gray')
        
        self.ax.set_xticks(range(1,len(self.x_labels)+1))
        self.ax.set_xticklabels(self.x_labels)
        
        canvas=FigureCanvas(self.fig)
        response=django.http.HttpResponse(content_type='image/png')
        canvas.print_png(response)
        return response
        
    