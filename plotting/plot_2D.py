#! /usr/bin/env python

import os
import glob
import math
import array
import sys
import time
import ROOT
from array import array

ROOT.gROOT.ProcessLine(".L ~/tdrstyle.C");
ROOT.setTDRStyle();
ROOT.gStyle.SetPadLeftMargin(0.16);
ROOT.gStyle.SetPadRightMargin(0.20);
ROOT.gStyle.SetPadTopMargin(0.10);
ROOT.gStyle.SetPalette(1);

## ===========================================================================================

def getAsymLimits(outpath,label,mass, cpsq, brnew):

    outputName = "higgsCombine_%s_%03i_%02i_%02i.Asymptotic.mH%03i.root" % (label,mass,cpsq,brnew,mass);
    file = "%s/%s" % (outpath,outputName);
    print file
    lims = [0]*6;
    
    if not os.path.isfile(file): 
        print "Warning (GetAsymLimits): "+file+" does not exist"
        return lims;

    f = ROOT.TFile(file);
    t = f.Get("limit");
    entries = t.GetEntries();

    for i in range(entries):

        t.GetEntry(i);
        t_quantileExpected = t.quantileExpected;
        t_limit = t.limit;

        #print "limit: ", t_limit, ", quantileExpected: ",t_quantileExpected;
        
        if t_quantileExpected == -1.: lims[0] = t_limit;
        elif t_quantileExpected >= 0.024 and t_quantileExpected <= 0.026: lims[1] = t_limit;
        elif t_quantileExpected >= 0.15 and t_quantileExpected <= 0.17: lims[2] = t_limit;            
        elif t_quantileExpected == 0.5: lims[3] = t_limit;            
        elif t_quantileExpected >= 0.83 and t_quantileExpected <= 0.85: lims[4] = t_limit;
        elif t_quantileExpected >= 0.974 and t_quantileExpected <= 0.976: lims[5] = t_limit;
        else: print "Unknown quantile!"

    return lims;

## ===========================================================================================
## ===========================================================================================
## ===========================================================================================

if __name__ == '__main__':

    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_052714/outputs";
    labels = "comb_4l+2l2v+lvlv+lvqq+2l2t";
    
    mass  = 700;
    cpsq  = [01,02,03,05,07,10];  
    brnew = [00,01,02,03,04,05];

    cpsqbin  = [0.05,0.15,0.25,0.4,0.6,0.85,1.15]; 
    brnewbin = [-0.05,0.05,0.15,0.25,0.35,0.45,0.55]; 
    limGrid = ROOT.TH2D("limGrid",";BR_{new};C\'^{2};#mu = #sigma_{95%CL}/#sigma_{SM}",6,array('d',cpsqbin),6,array('d',brnewbin))

    for i in range(len(brnew)):
        for j in range(len(cpsq)):
            
            gamFactor = (float(cpsq[j])/10.)/(1-(float(brnew[i])/10.));
            if gamFactor > 1: continue

            curlim = getAsymLimits(outpath,labels,mass,cpsq[j],brnew[i])
            if curlim[3] > 0: limGrid.SetBinContent(j+1,i+1,curlim[3]);

    banner = ROOT.TLatex(0.18,0.92,("CMS Preliminary, 7+8 TeV"));
    banner.SetNDC()
    banner.SetTextSize(0.035)

    banner2 = ROOT.TLatex(0.45,0.85,("4l+2l2v+lvlv+lvqq+2l2t"));
    banner2.SetNDC()
    banner2.SetTextSize(0.035)

    banner3 = ROOT.TLatex(0.6,0.80,("m_{H} = 700 GeV"));
    banner3.SetNDC()
    banner3.SetTextSize(0.035)
    
    can = ROOT.TCanvas("can","can",1000,800);
    hrl = can.DrawFrame(0.0,0.0,1.0,0.5);
    hrl.GetYaxis().SetTitle("BR_{new}");
    hrl.GetXaxis().SetTitle("C\'^{2}");  
    limGrid.Draw("colz same");
    banner.Draw();
    banner2.Draw();    
    banner3.Draw();        
    ROOT.gPad.RedrawAxis();
    can.SaveAs("test_2d_700.eps");

     





