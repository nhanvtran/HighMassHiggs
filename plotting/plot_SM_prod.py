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

    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_062414/outputs/";
    labels = ["combined","combined","combined","combined","combined","combined"];
    #labels = ["hzz2l2v"]*3;
    labelNames = ["full combination","full (expected)",
                  "gg #rightarrow H only","gg #rightarrow H only (exp)",
                  "qq #rightarrow Hqq only","qq #rightarrow Hqq only (exp)"];
    postfix = ["","","_ggf","_ggf","_vbf","_vbf"];
    expecteds = [2,4,6];    
    mass  = [200,250,300,350,400,500,600,700,800,900,1000];
    #mass  = [400];

    arrays_masses = [];
    arrays = [];
    for i in range(len(labels)):
        arrays_masses.append( array.array('d', []) )
        arrays.append( array.array('d', []) )
        
    for i in range(len(labels)):
        for j in range(len(mass)):
            # if postfix[i] == "":
            curlims = getAsymLimits(outpath,labels[i],mass[j],10,00,postfix[i]);
            curindex = 0;
            if i+1 in expecteds: curindex = 3;
            if curlims[3] > 0: 
                arrays_masses[i].append( mass[j] );
                arrays[i].append(curlims[curindex]);
            # else: 
            #     curlim = getMultiDimLimits(outpath,labels[i],postfix[i],mass[j],10,00);
            #     #print "curlim, multidim = ", curlim;
            #     if curlim > 0: arrays_masses[i].append( mass[j] );
            #     if curlim > 0: arrays[i].append(curlim);

    # make graphs
    graphs = [];
    for a in range(len(labels)):
        print len(arrays_masses[a])
        graphs.append( ROOT.TGraph( len(arrays_masses[a]), arrays_masses[a], arrays[a] ) );
        
	# plot...
    banner = ROOT.TLatex(0.20,0.92,("CMS Preliminary, #leq 5.0 fb^{-1} at #sqrt{s}=7 TeV, #leq 19.6 fb^{-1} at #sqrt{s}=8 TeV"));
    banner.SetNDC()
    banner.SetTextSize(0.035)

    colors = [1,1,4,4,6,6,2];
    widths = [2,2,2,2,2,2,3]; 
    styles = [1,2,1,2,1,2,3]; 
    leg = ROOT.TLegend(0.50,0.18,0.85,0.35);
    leg.SetFillStyle(1001);
    leg.SetFillColor(0);    
    leg.SetBorderSize(1);  
    leg.SetNColumns(2);
    for a in range(len(labels)):
        graphs[a].SetLineColor( colors[a] );        
        graphs[a].SetLineWidth( widths[a] );                    
        graphs[a].SetLineStyle( styles[a] );                            
        leg.AddEntry(graphs[a],labelNames[a],"l");
                                
    oneLine = ROOT.TF1("oneLine","1",199,1001);
    oneLine.SetLineColor(ROOT.kRed+2);
    oneLine.SetLineWidth(1);
    oneLine.SetLineStyle(2);
             
    can = ROOT.TCanvas("can","can",1200,800);
    hrl = can.DrawFrame(199,0.01,1001,15.);
    hrl.GetYaxis().SetTitle("#mu = #sigma_{95%CL}/#sigma_{SM}");
    hrl.GetXaxis().SetTitle("mass (GeV)");
    can.SetGrid(); 

    for a in range(len(labels)): 
#            graphs_2sigma[a].SetFillColor(ROOT.kYellow)
#            graphs_1sigma[a].SetFillColor(ROOT.kGreen)            
#            if a == 5: graphs_2sigma[a].Draw("f")
#            if a == 5: graphs_1sigma[a].Draw("f")            
        graphs[a].Draw("c");

    oneLine.Draw("LSAMES");
    banner.Draw();
    leg.Draw()
    ROOT.gPad.SetLogy();
    can.SaveAs("plots/combinedSM_prod.eps");       
    can.SaveAs("plots/combinedSM_prod.pdf");       




