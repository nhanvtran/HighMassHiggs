#! /usr/bin/env python

import os
import glob
import math
import array
import sys
import time
import ROOT
from plotUtils import *

ROOT.gROOT.ProcessLine(".L ~/tdrstyle.C");
ROOT.setTDRStyle();
ROOT.gStyle.SetPadLeftMargin(0.16);
ROOT.gStyle.SetPadRightMargin(0.10);
ROOT.gStyle.SetPadTopMargin(0.10);
ROOT.gStyle.SetPalette(1);

############################################
#            Job steering                  #
############################################
from optparse import OptionParser

parser = OptionParser()

parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
parser.add_option('--tag',action="store",type="string",dest="tag",default="combined")
#parser.add_option('--tag',action="store",type="string",dest="tag",default="qg")

(options, args) = parser.parse_args()


## ===========================================================================================
## ===========================================================================================
## ===========================================================================================

if __name__ == '__main__':

    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_081214/outputs";
    #labels = ["combined"];
    labels = [options.tag];
    mass  = [200,250,300,350,400,500,600,700,800,900,1000];
    #cpsq  = [01,02,03,05,07,10];
    cpsq  = [01,02,03,05,07,10];

    arrays_masses = [];
    arrays_envelo = [];    
    arrays = [];
    arrays_1sigma = [];
    arrays_2sigma = [];
    for i in range(len(cpsq)):
        arrays_masses.append( array.array('d', []) )
        arrays_envelo.append( array.array('d', []) )        
        arrays.append( array.array('d', []) )
        arrays_1sigma.append( array.array('d', []) )
        arrays_2sigma.append( array.array('d', []) )

    for i in range(len(cpsq)):
        for j in range(len(mass)):
            curlims = getAsymLimits(outpath,labels[0],mass[j],cpsq[i],00);
            if curlims[3] > 0: arrays_masses[i].append( mass[j] );
            if curlims[3] > 0: arrays_envelo[i].append( mass[j] );            
            if curlims[3] > 0: arrays[i].append(curlims[3]);
            if curlims[3] > 0: arrays_1sigma[i].append(curlims[2]);
            if curlims[3] > 0: arrays_2sigma[i].append(curlims[1]);


    print "reverse direction \n \n \n"


    for i in range(len(cpsq)):
        for j in range(len(mass)-1, -1, -1):
            curlims = getAsymLimits(outpath,labels[0],mass[j],cpsq[i],00);
            if curlims[3] > 0: arrays_1sigma[i].append(curlims[4]);
            if curlims[3] > 0: arrays_2sigma[i].append(curlims[5]);
            if curlims[3] > 0: arrays_envelo[i].append( mass[j] );            

    # make graphs
    graphs = [];
    graphs_1sigma = [];
    graphs_2sigma = [];                
    for a in range(len(cpsq)):
        graphs.append( ROOT.TGraph( len(arrays_masses[a]), arrays_masses[a], arrays[a] ) );
        graphs_1sigma.append( ROOT.TGraph( len(2*arrays_masses[a]), arrays_envelo[a], arrays_1sigma[a] ) );
        graphs_2sigma.append( ROOT.TGraph( len(2*arrays_masses[a]), arrays_envelo[a], arrays_2sigma[a] ) );

	# plot...
    colors = [1,4,6,7,3,46,2,8];
    widths = [2,2,2,2,2,2,2,2]; 
    leg = ROOT.TLegend(0.70,0.20,0.85,0.40);
    leg.SetFillStyle(1001);
    leg.SetFillColor(0);    
    leg.SetBorderSize(1);  
    for a in range(len(cpsq)):
        graphs[a].SetLineColor( colors[a] );        
        graphs[a].SetMarkerColor( colors[a] );   
        graphs[a].SetMarkerStyle( 24 );   
        graphs[a].SetLineWidth( widths[a] );                    
        leg.AddEntry(graphs[a],"C\'^{2} = "+str(cpsq[a]/10.),"pl");
                                
    banner = ROOT.TLatex(0.18,0.92,("CMS Preliminary, 7+8 TeV "));
    banner.SetNDC()
    banner.SetTextSize(0.035)

    banner2 = ROOT.TLatex(0.2,0.2,("combined: BR_{new} = 0"));
    banner2.SetNDC()
    banner2.SetTextSize(0.04)

    oneLine = ROOT.TF1("oneLine","1",199,1001);
    oneLine.SetLineColor(ROOT.kRed+2);
    oneLine.SetLineWidth(1);
    oneLine.SetLineStyle(2);
             
    can = ROOT.TCanvas("can","can",1200,800);
    hrl = can.DrawFrame(199,0.01,1001,25.);
    hrl.GetYaxis().SetTitle("#mu = #sigma_{95%CL}/#sigma_{SM}");
    hrl.GetXaxis().SetTitle("mass (GeV)");
    can.SetGrid(); 

    for a in range(len(cpsq)): 
#            graphs_2sigma[a].SetFillColor(ROOT.kYellow)
#            graphs_1sigma[a].SetFillColor(ROOT.kGreen)            
#            if a == 5: graphs_2sigma[a].Draw("f")
#            if a == 5: graphs_1sigma[a].Draw("f")            
        graphs[a].Draw("PL");

    oneLine.Draw("LSAMES");
    leg.Draw();
    banner.Draw();
    banner2.Draw();    
    ROOT.gPad.SetLogy();
    can.SaveAs("plots/test_BRnew00-"+options.tag+"_081214.eps");       
    can.SaveAs("plots/test_BRnew00-"+options.tag+"_081214.pdf");       




