#! /usr/bin/env python

import os
import glob
import math
import array
import sys
import time
import ROOT
from array import array

from plotUtils import *

ROOT.gROOT.ProcessLine(".L ~/tdrstyle.C");
ROOT.setTDRStyle();
ROOT.gStyle.SetPadLeftMargin(0.16);
ROOT.gStyle.SetPadRightMargin(0.10);
ROOT.gStyle.SetPadTopMargin(0.10);
ROOT.gStyle.SetPalette(1);

## ===========================================================================================
## ===========================================================================================
## ===========================================================================================

if __name__ == '__main__':

    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_052814/outputs/";
    labels = ["hww2l2v","hwwlvqq","hzz2l2v","hzzllll","hzz2l2t","hzz2l2q","combined"];
    mass  = [200,250,300,350,400,500,600,700,800,900,1000];

    arrays_masses = [];
    arrays_envelo = [];    
    arrays = [];
    arrays_1sigma = [];
    arrays_2sigma = [];
    for i in range(len(labels)):
        arrays_masses.append( array.array('d', []) )
        arrays_envelo.append( array.array('d', []) )        
        arrays.append( array.array('d', []) )
        arrays_1sigma.append( array.array('d', []) )
        arrays_2sigma.append( array.array('d', []) )

    for i in range(len(labels)):
        for j in range(len(mass)):
            curlims = getAsymLimits(outpath,labels[i],mass[j],10,00);
            if curlims[3] > 0: arrays_masses[i].append( mass[j] );
            if curlims[3] > 0: arrays_envelo[i].append( mass[j] );            
            if curlims[3] > 0: arrays[i].append(curlims[3]);
            if curlims[3] > 0: arrays_1sigma[i].append(curlims[2]);
            if curlims[3] > 0: arrays_2sigma[i].append(curlims[1]);
            print curlims

    print "reverse direction";

    for i in range(len(labels)):
        for j in range(len(mass)-1, -1, -1):
            curlims = getAsymLimits(outpath,labels[i],mass[j],10,00);
            if curlims[3] > 0: arrays_1sigma[i].append(curlims[4]);
            if curlims[3] > 0: arrays_2sigma[i].append(curlims[5]);
            if curlims[3] > 0: arrays_envelo[i].append( mass[j] );            

    # make graphs
    graphs = [];
    graphs_1sigma = [];
    graphs_2sigma = [];                
    for a in range(len(labels)):
        print len(arrays_masses[a])
        graphs.append( ROOT.TGraph( len(arrays_masses[a]), arrays_masses[a], arrays[a] ) );
        graphs_1sigma.append( ROOT.TGraph( len(2*arrays_masses[a]), arrays_envelo[a], arrays_1sigma[a] ) );
        graphs_2sigma.append( ROOT.TGraph( len(2*arrays_masses[a]), arrays_envelo[a], arrays_2sigma[a] ) );

	# plot...
    colors = [1,4,6,7,3,46,2];
    widths = [2,2,2,2,2,2,3]; 
    leg = ROOT.TLegend(0.60,0.12,0.85,0.35);
    leg.SetFillStyle(1001);
    leg.SetFillColor(0);    
    leg.SetBorderSize(1);  
    for a in range(len(labels)):
        graphs[a].SetLineColor( colors[a] );        
        graphs[a].SetLineWidth( widths[a] );                    
        leg.AddEntry(graphs[a],labels[a],"l");
                                
    oneLine = ROOT.TF1("oneLine","1",199,1001);
    oneLine.SetLineColor(ROOT.kRed+2);
    oneLine.SetLineWidth(1);
    oneLine.SetLineStyle(2);
             
    can = ROOT.TCanvas("can","can",1200,800);
    hrl = can.DrawFrame(199,0.05,1001,15.);
    hrl.GetYaxis().SetTitle("#mu = #sigma_{95%CL}/#sigma_{SM}");
    hrl.GetXaxis().SetTitle("mass (GeV)");
    can.SetGrid(); 

    for a in range(len(labels)): 
#            graphs_2sigma[a].SetFillColor(ROOT.kYellow)
#            graphs_1sigma[a].SetFillColor(ROOT.kGreen)            
#            if a == 5: graphs_2sigma[a].Draw("f")
#            if a == 5: graphs_1sigma[a].Draw("f")            
        graphs[a].Draw();

    oneLine.Draw("LSAMES");
    leg.Draw()
    ROOT.gPad.SetLogy();
    can.SaveAs("test.eps");       





