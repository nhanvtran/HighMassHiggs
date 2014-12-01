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
#ROOT.gStyle.SetPadRightMargin(0.20);
ROOT.gStyle.SetPadTopMargin(0.10);
ROOT.gStyle.SetPalette(1);

############################################
#            Job steering                  #
############################################
from optparse import OptionParser

parser = OptionParser()

parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
parser.add_option('--full',action="store_true",dest="full",default=False,help='do training')
parser.add_option('--ggf',action="store_true",dest="ggf",default=False,help='do training')
parser.add_option('--vbf',action="store_true",dest="vbf",default=False,help='do training')
parser.add_option('--WW',action="store_true",dest="WW",default=False,help='do training')
parser.add_option('--ZZ',action="store_true",dest="ZZ",default=False,help='do training')

(options, args) = parser.parse_args()

############################################################

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
    postfix = "";
    if options.full: 
        labels = "combined_BSM";
        postfix = "";
    if options.ggf:
        labels = "combined_BSM_ggF";
        postfix = "_ggf";
    if options.vbf:
        labels = "combined_BSM_vbf";
        postfix = "_vbf";
    if options.WW:
        labels = "combined_WW_SM";
        postfix = "";
    if options.ZZ:
        labels = "combined_ZZ_SM";
        postfix = "";

    #labels = "hzz2l2v";
    mass  = [145,150,160,170,180,190,200,250,300,350,400,500,600,700,800,900,1000];
    cpsq  = [00,30,50,01,02,03,05,07,10];

    cpsqbin  = [0.00,0.02,0.04,0.07,0.13,0.25,0.4,0.6,0.85,1.15];  
    massbin = [142.5,147.5,155,165,175,185,195,225,275,325,375,450,550,650,750,850,950,1050];
    
    if options.WW: mass  = [200,250,300,350,400,500,600,700,800,900,1000];
    if options.WW: massbin = [175,225,275,325,375,450,550,650,750,850,950,1050];
    if options.WW: cpsq  = [01,02,03,05,07,10];
    if options.WW: cpsqbin  = [0.07,0.13,0.25,0.4,0.6,0.85,1.15];  

    limGrid0_obs = ROOT.TH2D( "limGrid0_obs",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",len(mass),array.array('d',massbin),len(cpsq),array.array('d',cpsqbin) );
    limGrid0_exp = ROOT.TH2D( "limGrid0_exp",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",len(mass),array.array('d',massbin),len(cpsq),array.array('d',cpsqbin) );

    limGrid2_obs = ROOT.TH2D( "limGrid2_obs",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",len(mass),array.array('d',massbin),len(cpsq),array.array('d',cpsqbin) );
    limGrid2_exp = ROOT.TH2D( "limGrid2_exp",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",len(mass),array.array('d',massbin),len(cpsq),array.array('d',cpsqbin) );

    limGrid5_obs = ROOT.TH2D( "limGrid5_obs",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",len(mass),array.array('d',massbin),len(cpsq),array.array('d',cpsqbin) );
    limGrid5_exp = ROOT.TH2D( "limGrid5_exp",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",len(mass),array.array('d',massbin),len(cpsq),array.array('d',cpsqbin) );

    # limGrid1 = ROOT.TH2D( "limGrid1",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );
    # limGrid2 = ROOT.TH2D( "limGrid2",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );
    # limGrid3 = ROOT.TH2D( "limGrid3",";mass (GeV);C\'^{2};#mu = #sigma_{95\%CL}/#sigma_{SM}",9,array.array('d',massbin),6,array.array('d',cpsqbin) );

    for i in range(len(mass)):
        for j in range(len(cpsq)):

            curlim = getAsymLimits(outpath,labels,mass[i],cpsq[j],00,postfix)
            limGrid0_exp.SetBinContent(i+1,j+1,curlim[3]);
            limGrid0_obs.SetBinContent(i+1,j+1,curlim[0]);            
            curlim = getAsymLimits(outpath,labels,mass[i],cpsq[j],02,postfix)
            limGrid2_exp.SetBinContent(i+1,j+1,curlim[3]);
            limGrid2_obs.SetBinContent(i+1,j+1,curlim[0]);            
            curlim = getAsymLimits(outpath,labels,mass[i],cpsq[j],05,postfix)
            limGrid5_exp.SetBinContent(i+1,j+1,curlim[3]);
            limGrid5_obs.SetBinContent(i+1,j+1,curlim[0]);            

            # curlim1 = getAsymLimits(outpath,labels,mass[i],cpsq[j],01)            
            # curlim2 = getAsymLimits(outpath,labels,mass[i],cpsq[j],02)               
            # curlim3 = getAsymLimits(outpath,labels,mass[i],cpsq[j],03)            
            # limGrid1.SetBinContent(i+1,j+1,curlim1[3]);
            # limGrid2.SetBinContent(i+1,j+1,curlim2[3]);
            # limGrid3.SetBinContent(i+1,j+1,curlim3[3]);

    banner = ROOT.TLatex(0.17,0.92,("CMS"));
    banner.SetNDC();
    banner.SetTextSize(0.040);
    bax = 0.50;
    if options.full: bax = 0.6;
    bannerA = ROOT.TLatex(bax,0.92,("#leq 5.0 fb^{-1} (7 TeV), #leq 19.6 fb^{-1} (8 TeV)"));
    bannerA.SetNDC()
    bannerA.SetTextSize(0.040);

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
    limGridGr5_exp = ROOT.TGraph2D(limGrid5_exp);
    if not options.WW and not options.vbf:
        cont5_obs = GetContours(limGridGr5_obs);
        cont5_exp = GetContours(limGridGr5_exp);

    lxlo1 = 0.22; lylo1 = 0.71; lxhi1 = 0.42; lyhi1 = 0.86;
    lxlo2 = 0.45; lylo2 = 0.71; lxhi2 = 0.65; lyhi2 = 0.86;
    if options.WW or options.vbf:
        lxlo1 = 0.66; lylo1 = 0.40; lxhi1 = 0.92; lyhi1 = 0.55;
        lxlo2 = 0.66; lylo2 = 0.25; lxhi2 = 0.92; lyhi2 = 0.40;


    legtextsize = 0.027;
    if options.full: legtextsize = 0.035;
    leg = ROOT.TLegend(lxlo1,lylo1,lxhi1,lyhi1);
    leg.SetFillStyle(0);
    leg.SetFillColor(0);    
    leg.SetBorderSize(0);
    leg.SetTextSize(legtextsize);  
    leg.AddEntry(cont0_obs[0],"Obs., BR_{new} = 0.0              ","L");
    leg.AddEntry(cont2_obs[0],"Obs., BR_{new} = 0.2              ","L");
    if not options.WW and not options.vbf: leg.AddEntry(cont5_obs[0],"Obs., BR_{new} = 0.5              ","L");
    leg2 = ROOT.TLegend(lxlo2,lylo2,lxhi2,lyhi2);
    leg2.SetFillStyle(0);
    leg2.SetFillColor(0);    
    leg2.SetBorderSize(0);
    leg2.SetTextSize(legtextsize);  
    leg2.AddEntry(cont0_exp[0],"Exp., BR_{new} = 0.0              ","L");
    leg2.AddEntry(cont2_exp[0],"Exp., BR_{new} = 0.2              ","L");
    if not options.WW and not options.vbf: leg2.AddEntry(cont5_exp[0],"Exp., BR_{new} = 0.5              ","L");

    canW = 1200;
    canH = 1000;
    if options.full: 
        canW = 1600;
        canH = 1000;
    xlo = 144;
    if options.WW: xlo = 199
    ylo = 0.0;
    can = ROOT.TCanvas("can","can",canW,canH);
    hrl = can.DrawFrame(xlo,ylo,1001,0.7);
    #hrl.SetTitle(";mass (GeV);C\' ^{2};#mu = #sigma_{95%CL}/#sigma_{BSM}")
    hrl.SetTitle(";mass (GeV);C\' ^{2}")
    hrl.GetXaxis().SetMoreLogLabels();
    hrl.GetXaxis().SetNoExponent();
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

    if not options.WW and not options.vbf:
        for i in range(len(cont5_obs)): 
            cont5_obs[i].SetLineWidth(2);
            cont5_obs[i].SetLineColor(4);
            cont5_obs[i].Draw("L");

        for i in range(len(cont5_exp)): 
            cont5_exp[i].SetLineWidth(2);
            cont5_exp[i].SetLineColor(4);
            cont5_exp[i].SetLineStyle(2);
            cont5_exp[i].Draw("L");

    oneLine = ROOT.TF1("oneLine","0.5",145,1000);
    oneLine.SetLineColor(4);
    oneLine.SetLineWidth(1);
    oneLine.SetLineStyle(5);
    if not options.WW and not options.vbf: oneLine.Draw("sames");        
    b4x = 0.35;
    b4y = 0.65;
    if options.full: 
        b4x = 0.01;
        b4y = 0.69;
    banner4 = ROOT.TLatex(b4x,b4y,("#Gamma > #Gamma_{SM} (BR_{new} = 0.5)"));
    banner4.SetNDC()
    banner4.SetTextSize(0.025)
    banner4.SetTextColor(4)
    if not options.WW and not options.vbf: banner4.Draw();

    constrLine = ROOT.TF1("constrLine","0.26",145,1000);
    constrLine.SetLineColor(ROOT.kGray+1);
    constrLine.SetLineWidth(1);
    constrLine.SetLineStyle(5);
    if options.full: constrLine.Draw("sames");      
    banner5 = ROOT.TLatex(0.01,0.42,("#uparrow #mu_{h125} = 1.00 #pm 0.13 #uparrow"));
    banner5.SetNDC()
    banner5.SetTextSize(0.025)
    banner5.SetTextColor(ROOT.kGray+1)
    if options.full: banner5.Draw();

    channelText = "";
    if options.WW: channelText = "H #rightarrow WW only";
    if options.ZZ: channelText = "H #rightarrow ZZ only";
    if options.ggf: channelText = "gg #rightarrow H only";
    if options.vbf: channelText = "qq #rightarrow Hqq only";
    banner6 = ROOT.TLatex(0.72,0.18,(channelText));
    banner6.SetNDC()
    banner6.SetTextSize(0.038)
    banner6.SetTextColor(ROOT.kGray+3)
    if options.ZZ or options.WW or options.ggf or options.vbf: banner6.Draw();


    banner.Draw();
    bannerA.Draw();    
    leg.Draw();
    leg2.Draw();
    #banner3.Draw();     
    #limGridGraph.Draw("cont same");   
    ROOT.gPad.SetLogz();
    ROOT.gPad.SetLogx();
    ROOT.gPad.RedrawAxis();    
    can.Update();

    if options.WW: postfix = "_WW";
    if options.ZZ: postfix = "_ZZ";
    can.SaveAs("plots/combined_BRnewContours"+postfix+".eps");  
    can.SaveAs("plots/combined_BRnewContours"+postfix+".pdf");  





