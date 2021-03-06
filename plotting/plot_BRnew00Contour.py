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
def GetContours( th2 ):

    limGridGraph = ROOT.TGraph2D(th2);    
    contours = [1.0];
    limGridGraph.GetHistogram().SetContour(1,array.array('d',contours));
    limGridGraph.Draw("cont z list"); 

    contLevel = limGridGraph.GetContourList(1.0);
    print "N contours = ",contLevel.GetSize();
    contours = [];
    for i in range(contLevel.GetSize()):
        contours.append( contLevel.At(i) );
    return contours;

## ===========================================================================================
if __name__ == '__main__':

    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_102614/outputs";
    labels = "combined_BSM";
    #labels = "hzz2l2v";
    mass  = [200,250,300,350,400,500,600,700,800,900,1000];
    cpsq  = [01,02,03,05,07,10];

    cpsqbin  = [0.05,0.15,0.25,0.4,0.6,0.85,1.15];  
    massbin = [150,250,350,450,550,650,750,850,950,1050];
    limGrid = ROOT.TH2D( "limGrid",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );
    limGrid1 = ROOT.TH2D( "limGrid1",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );
    limGrid2 = ROOT.TH2D( "limGrid2",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );
    limGrid3 = ROOT.TH2D( "limGrid3",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );

    for i in range(len(mass)):
        for j in range(len(cpsq)):

            curlim = getAsymLimits(outpath,labels,mass[i],cpsq[j],00)
            limGrid.SetBinContent(i+1,j+1,curlim[3]);

            # curlim1 = getAsymLimits(outpath,labels,mass[i],cpsq[j],01)            
            # curlim2 = getAsymLimits(outpath,labels,mass[i],cpsq[j],02)               
            # curlim3 = getAsymLimits(outpath,labels,mass[i],cpsq[j],03)            
            # limGrid1.SetBinContent(i+1,j+1,curlim1[3]);
            # limGrid2.SetBinContent(i+1,j+1,curlim2[3]);
            # limGrid3.SetBinContent(i+1,j+1,curlim3[3]);

    banner = ROOT.TLatex(0.20,0.92,("CMS Preliminary, #leq 5.0 fb^{-1} at #sqrt{s}=7 TeV, #leq 19.6 fb^{-1} at #sqrt{s}=8 TeV"));
    banner.SetNDC()
    banner.SetTextSize(0.035)

    banner2 = ROOT.TLatex(0.92,0.88,("#mu = #sigma_{95\%CL}/#sigma_{BSM}"));
    banner2.SetNDC()
    banner2.SetTextSize(0.065)
    banner2.SetTextAngle(270);

    banner3 = ROOT.TLatex(0.6,0.80,("m_{H} = 300 GeV"));
    banner3.SetNDC()
    banner3.SetTextSize(0.035)
        
    limGridGr = ROOT.TGraph2D(limGrid);
    contours = GetContours(limGrid);

    leg = ROOT.TLegend(0.25,0.75,0.60,0.85);
    leg.SetFillStyle(0);
    leg.SetFillColor(0);    
    leg.SetBorderSize(0);  
    leg.AddEntry(contours[1],"Expected 95% CL limit","L");

    # contours1 = GetContours(limGrid1);
    # contours2 = GetContours(limGrid2);
    # contours3 = GetContours(limGrid3);

    can = ROOT.TCanvas("can","can",1600,1000);
    hrl = can.DrawFrame(199,0.1,1001,0.7);
    hrl.SetTitle(";mass (GeV);C\' ^{2}, BR_{new} = 0;#mu = #sigma_{95%CL}/#sigma_{BSM}")
    #hrl.GetZaxis().RotateTitle(0); 
    # hrl.GetZaxis().SetTitle("#mu = #sigma_{95%CL}/#sigma_{BSM}");
    # hrl.GetZaxis().SetTitleOffset(0.);
    # hrl.GetXaxis().SetTitle("mass (GeV)");
    # hrl.GetYaxis().SetTitle("C\' ^{2}, BR_{new} = 0");    
    #limGrid.Smooth(1);
    limGridGr.Draw("colz same");
    for i in range(len(contours)): 
        contours[i].SetLineWidth(2);
        contours[i].Draw("L");

    # for i in range(len(contours1)): contours1[i].Draw("L");
    # for i in range(len(contours2)): contours2[i].Draw("L");   
    # for i in range(len(contours3)): contours3[i].Draw("L");

    banner.Draw();
    banner2.Draw();    
    leg.Draw();
    #banner3.Draw();     
    #limGridGraph.Draw("cont same");   
    ROOT.gPad.SetLogz();
    ROOT.gPad.RedrawAxis();    
    can.Update();
    can.SaveAs("plots/combined_BRnew00Contour.eps");  
    can.SaveAs("plots/combined_BRnew00Contour.pdf");  





