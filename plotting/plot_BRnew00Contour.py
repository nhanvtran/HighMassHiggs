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
ROOT.gStyle.SetPadLeftMargin(0.20);
ROOT.gStyle.SetPadRightMargin(0.20);
ROOT.gStyle.SetPadTopMargin(0.10);
ROOT.gStyle.SetPalette(1);

## ===========================================================================================
## ===========================================================================================
## ===========================================================================================

if __name__ == '__main__':

    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_052714/outputs";
    labels = "comb_4l+2l2v+lvlv+lvqq+2l2t";
    #labels = "hzz2l2v";
    mass  = [200,300,400,500,600,700,800,900,1000];
    cpsq  = [01,02,03,05,07,10];

    cpsqbin  = [0.05,0.15,0.25,0.4,0.6,0.85,1.15];  
    massbin = [150,250,350,450,550,650,750,850,950,1050];
    limGrid = ROOT.TH2D( "limGrid",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );


    for i in range(len(mass)):
        for j in range(len(cpsq)):

            curlim = getAsymLimits(outpath,labels,mass[i],cpsq[j],00)
            limGrid.SetBinContent(i+1,j+1,curlim[3]);

    banner = ROOT.TLatex(0.25,0.92,("CMS Preliminary, 7+8 TeV"));
    banner.SetNDC()
    banner.SetTextSize(0.035)

    banner2 = ROOT.TLatex(0.45,0.85,("WWlvlv+ZZ2l2v+WWlvqq"));
    banner2.SetNDC()
    banner2.SetTextSize(0.035)

    banner3 = ROOT.TLatex(0.6,0.80,("m_{H} = 300 GeV"));
    banner3.SetNDC()
    banner3.SetTextSize(0.035)
        
    limGridGraph = ROOT.TGraph2D(limGrid);
    contours = [0.5];
    limGridGraph.GetHistogram().SetContour(1,array.array('d',contours));
    limGridGraph.Draw("cont list");   
    contLevel = limGridGraph.GetContourList(0.5);
    print contLevel.GetSize();
    contour = contLevel.First();

    can = ROOT.TCanvas("can","can",1600,1000);
    hrl = can.DrawFrame(199,0.1,1001,1.0);
    hrl.GetZaxis().RotateTitle(0); 
    hrl.GetZaxis().SetTitle("#mu = #sigma_{95%CL}/#sigma_{SM}");
    hrl.GetXaxis().SetTitle("mass (GeV)");
    hrl.GetYaxis().SetTitle("C\'^{2}");    
    limGrid.Smooth(1);
    limGrid.Draw("colz same");
    contour.Draw("L");
    banner.Draw();
    #banner2.Draw();    
    #banner3.Draw();     
    #limGridGraph.Draw("cont same");   
    ROOT.gPad.SetLogz();
    ROOT.gPad.RedrawAxis();    
    can.Update();
    can.SaveAs("test_BRnew00Contour.eps");  





