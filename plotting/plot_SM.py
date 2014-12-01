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

    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_102614/outputs/";
    legends = ["H #rightarrow WW #rightarrow 2l2#nu",
                "H #rightarrow WW #rightarrow l#nu qq",
                "H #rightarrow ZZ #rightarrow 2l2#nu",
                "H #rightarrow ZZ #rightarrow 4l",
                "H #rightarrow ZZ #rightarrow 2l2#tau",
                "H #rightarrow ZZ #rightarrow 2l2q",
                "Combined",
                "Combined (exp)"];
                #"H #rightarrow WW #rightarrow 2l2#nu (exp)",
                #"H #rightarrow ZZ #rightarrow 4l (exp)"];
    labels = ["hww2l2v","hwwlvqq","hzz2l2v","hzz4l","hzz2l2t","hzz2l2q","combined_all","combined_all"];#,"hww2l2v_h125bkg","hzz4l"];
    expecteds = [8,9,10];
    mass  = [145,150,160,170,180,190,200,250,300,350,400,500,600,700,800,900,1000];
    #mass  = [200,250,300,350,400,500,600,700,800,900,1000];
    drawBands = [8];

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
            curindex = 0;
            if i+1 in expecteds: curindex = 3;
	    
            if curlims[3] > 0: arrays_masses[i].append( mass[j] );
            if curlims[3] > 0: arrays_envelo[i].append( mass[j] );            
            if curlims[3] > 0: arrays[i].append(curlims[curindex]);
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
        print labels[a], ",", len(arrays_masses[a])
        graphs.append( ROOT.TGraph( len(arrays_masses[a]), arrays_masses[a], arrays[a] ) );
        graphs_1sigma.append( ROOT.TGraph( len(2*arrays_masses[a]), arrays_envelo[a], arrays_1sigma[a] ) );
        graphs_2sigma.append( ROOT.TGraph( len(2*arrays_masses[a]), arrays_envelo[a], arrays_2sigma[a] ) );

	# plot...
    banner = ROOT.TLatex(0.17,0.92,("CMS"));
    banner.SetNDC();
    banner.SetTextSize(0.040);
    banner2 = ROOT.TLatex(0.50,0.92,("#leq 5.0 fb^{-1} (7 TeV), #leq 19.6 fb^{-1} (8 TeV)"));
    banner2.SetNDC()
    banner2.SetTextSize(0.040);

    colors = [1,4,6,7,3,46,2,2,1,7];
    widths = [2,2,2,2,2,2,3,2,2,3]; 
    styles = [1,1,1,1,1,1,1,2,2,2];

    leg = ROOT.TLegend(0.20,0.68,0.6,0.85);
    leg.SetFillStyle(1001);
    leg.SetFillColor(0);    
    leg.SetBorderSize(1);  
    leg.SetNColumns(2);
    for a in range(len(labels)):
        graphs[a].SetLineColor( colors[a] );        
        graphs[a].SetLineWidth( widths[a] );
        graphs[a].SetLineStyle( styles[a] );                    
        leg.AddEntry(graphs[a],legends[a],"l");
                                
    oneLine = ROOT.TF1("oneLine","1",145,1000);
    oneLine.SetLineColor(ROOT.kRed+2);
    oneLine.SetLineWidth(1);
    oneLine.SetLineStyle(2);
             
    can = ROOT.TCanvas("can","can",1200,800);
    hrl = can.DrawFrame(144,0.01,1001,100.);
    hrl.GetYaxis().SetTitle("#mu = #sigma_{95%CL}/#sigma_{SM}");
    hrl.GetXaxis().SetTitle("mass (GeV)");
    can.SetGrid(); 

    for a in range(len(labels)): 
        if a+1 in drawBands: 
            graphs_2sigma[a].SetFillColor(ROOT.kYellow);
            graphs_2sigma[a].SetFillStyle(3244);
            graphs_2sigma[a].Draw("f");
            leg.AddEntry(graphs_2sigma[a],"Combined (exp) 2 #sigma","f");

    for a in range(len(labels)): 
        print labels[a]
        graphs[a].Draw("c");

    oneLine.Draw("LSAMES");
    banner.Draw();
    banner2.Draw();
    leg.Draw()
    ROOT.gPad.SetLogy();
    pf = "def";
    can.SaveAs("plots/combinedSM_"+pf+".eps");       
    can.SaveAs("plots/combinedSM_"+pf+".png");           
    can.SaveAs("plots/combinedSM_"+pf+".pdf");           





