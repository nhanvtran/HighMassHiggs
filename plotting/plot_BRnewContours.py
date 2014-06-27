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

    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_062414/outputs";
    labels = "combined";
    #labels = "hzz2l2v";
    mass  = [200,250,300,350,400,500,600,700,800,900,1000];
    cpsq  = [01,02,03,05,07,10];

    cpsqbin  = [0.05,0.15,0.25,0.4,0.6,0.85,1.15];  
    massbin = [150,250,350,450,550,650,750,850,950,1050];
    limGrid0_obs = ROOT.TH2D( "limGrid0_obs",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );
    limGrid0_exp = ROOT.TH2D( "limGrid0_exp",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );

    limGrid2_obs = ROOT.TH2D( "limGrid2_obs",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );
    limGrid2_exp = ROOT.TH2D( "limGrid2_exp",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );

    limGrid5_obs = ROOT.TH2D( "limGrid5_obs",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );
    limGrid5_exp = ROOT.TH2D( "limGrid5_exp",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );

    # limGrid1 = ROOT.TH2D( "limGrid1",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );
    # limGrid2 = ROOT.TH2D( "limGrid2",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );
    # limGrid3 = ROOT.TH2D( "limGrid3",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );

    for i in range(len(mass)):
        for j in range(len(cpsq)):

            curlim = getAsymLimits(outpath,labels,mass[i],cpsq[j],00)
            limGrid0_exp.SetBinContent(i+1,j+1,curlim[3]);
            limGrid0_obs.SetBinContent(i+1,j+1,curlim[0]);            
            curlim = getAsymLimits(outpath,labels,mass[i],cpsq[j],02)
            limGrid2_exp.SetBinContent(i+1,j+1,curlim[3]);
            limGrid2_obs.SetBinContent(i+1,j+1,curlim[0]);            
            curlim = getAsymLimits(outpath,labels,mass[i],cpsq[j],05)
            limGrid5_exp.SetBinContent(i+1,j+1,curlim[3]);
            limGrid5_obs.SetBinContent(i+1,j+1,curlim[0]);            

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
        
    limGridGr0_obs = ROOT.TGraph2D(limGrid0_obs);
    cont0_obs = GetContours(limGridGr0_obs);
    limGridGr0_exp = ROOT.TGraph2D(limGrid0_exp);
    cont0_exp = GetContours(limGridGr0_exp);

    limGridGr2_obs = ROOT.TGraph2D(limGrid2_obs);
    cont2_obs = GetContours(limGridGr2_obs);
    limGridGr2_exp = ROOT.TGraph2D(limGrid2_exp);
    cont2_exp = GetContours(limGridGr2_exp);

    limGridGr5_obs = ROOT.TGraph2D(limGrid5_obs);
    cont5_obs = GetContours(limGridGr5_obs);
    limGridGr5_exp = ROOT.TGraph2D(limGrid5_exp);
    cont5_exp = GetContours(limGridGr5_exp);

    leg = ROOT.TLegend(0.25,0.6,0.60,0.85);
    leg.SetFillStyle(0);
    leg.SetFillColor(0);    
    leg.SetBorderSize(0);  
    leg.AddEntry(cont0_obs[0],"Observed, BR_{new} = 0.0","L");
    leg.AddEntry(cont0_exp[0],"Expected, BR_{new} = 0.0","L");
    leg.AddEntry(cont2_obs[0],"Observed, BR_{new} = 0.2","L");
    leg.AddEntry(cont2_exp[0],"Expected, BR_{new} = 0.2","L");
    leg.AddEntry(cont5_obs[0],"Observed, BR_{new} = 0.5","L");
    leg.AddEntry(cont5_exp[0],"Expected, BR_{new} = 0.5","L");

    can = ROOT.TCanvas("can","can",1600,1000);
    hrl = can.DrawFrame(199,0.1,1001,0.7);
    hrl.SetTitle(";mass (GeV);C\' ^{2}, BR_{new} = 0;#mu = #sigma_{95%CL}/#sigma_{BSM}")
    #hrl.GetZaxis().RotateTitle(0); 
    # hrl.GetZaxis().SetTitle("#mu = #sigma_{95%CL}/#sigma_{BSM}");
    # hrl.GetZaxis().SetTitleOffset(0.);
    # hrl.GetXaxis().SetTitle("mass (GeV)");
    # hrl.GetYaxis().SetTitle("C\' ^{2}, BR_{new} = 0");    
    #limGrid.Smooth(1);
    #limGridGr.Draw("colz same");

    for i in range(len(cont0_obs)): 
        cont0_obs[i].SetLineWidth(2);
        cont0_obs[i].Draw("L");

    for i in range(len(cont0_exp)): 
        cont0_exp[i].SetLineWidth(2);
        cont0_exp[i].SetLineStyle(2);
        cont0_exp[i].Draw("L");

    for i in range(len(cont2_obs)): 
        cont2_obs[i].SetLineWidth(2);
        cont2_obs[i].SetLineColor(2);
        cont2_obs[i].Draw("L");

    for i in range(len(cont2_exp)): 
        cont2_exp[i].SetLineWidth(2);
        cont2_exp[i].SetLineColor(2);
        cont2_exp[i].SetLineStyle(2);
        cont2_exp[i].Draw("L");

    for i in range(len(cont5_obs)): 
        cont5_obs[i].SetLineWidth(2);
        cont5_obs[i].SetLineColor(4);
        cont5_obs[i].Draw("L");

    for i in range(len(cont5_exp)): 
        cont5_exp[i].SetLineWidth(2);
        cont5_exp[i].SetLineColor(4);
        cont5_exp[i].SetLineStyle(2);
        cont5_exp[i].Draw("L");

    banner.Draw();
    banner2.Draw();    
    leg.Draw();
    #banner3.Draw();     
    #limGridGraph.Draw("cont same");   
    ROOT.gPad.SetLogz();
    ROOT.gPad.RedrawAxis();    
    can.Update();
    can.SaveAs("plots/combined_BRnewContours.eps");  
    can.SaveAs("plots/combined_BRnewContours.pdf");  





