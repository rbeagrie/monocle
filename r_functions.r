library(cummeRbund)
cuff<-readCufflinks(dir='E:/Rob/Bioinformatics/Monocle')

GenePlot <- function(gene_id,filename) { 
   print(gene_id)
   myGene <- getGene(cuff, gene_id)
   print(isoforms(myGene))
   png(filename=filename, height=400, width=700, bg="white") 
   
   gplot <- expressionPlot(myGene)
   print(gplot)
   dev.off()
}

IsoformPlot <- function(gene_id,filename) { 
   print(gene_id)
   myGene <- getGene(cuff, gene_id)
   print(isoforms(myGene))
   png(filename=filename, height=400, width=700, bg="white") 
   
   gplot <- expressionPlot(isoforms(myGene),showErrorbars=FALSE)
   print(gplot)
   dev.off()
}

TSSPlot <- function(gene_id,filename) { 
   print(gene_id)
   myGene <- getGene(cuff, gene_id)
   print(isoforms(myGene))
   png(filename=filename, height=400, width=700, bg="white") 
   
   gplot <- expressionPlot(myGene@TSS,showErrorbars=FALSE)
   print(gplot)
   dev.off()
}

args <- commandArgs(TRUE)

if(args[2] == 'gene'){
GenePlot(args[3],args[4])
}else{
if(args[2] == 'isoform'){
IsoformPlot(args[3],args[4])
}else{
if(args[2] == 'tss'){
TSSPlot(args[3],args[4])
}}}