#! /usr/bin/env python

import os
import glob
import math
import array
import sys
import time
import ROOT
from array import array

from hmhUtils import *

############################################
#            Job steering                  #
############################################
from optparse import OptionParser

parser = OptionParser()

parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
parser.add_option('--createWorkspace',action="store_true",dest="createWorkspace",default=False,help='do training')
parser.add_option('--runLimits',action="store_true",dest="runLimits",default=False,help='do training')

(options, args) = parser.parse_args()

############################################################

#--------------------------------------------------

if __name__ == '__main__':

    abspath = "/uscms_data/d2/ntran/physics/HighMassHiggs/svn/highmass2014"
    tmpdir  = "tmp"
    masses = [600,700,800,900,1000];
    #masses = [600];    
    
    nMasses       = len(masses);
    masses_array  = array.array('d', [])
    EL_hzz2l2v_0s = array.array('d', [])
    EL_hzz2l2t_0s = array.array('d', [])
    EL_hzz2l2q_0s = array.array('d', [])
    EL_hwwlvqq_0s = array.array('d', [])
    
    for i in range(len(masses)):
        
        masses_array.append( masses[i] );

        cur_hzz2l2v = chanWP(abspath,"hzz2l2v",masses[i],10,00);
        cur_hzz2l2t = chanWP(abspath,"hzz2l2t",masses[i],10,00);
        cur_hzz2l2q = chanWP(abspath,"hzz2l2q",masses[i],10,00);
        cur_hwwlvqq = chanWP(abspath,"hwwlvqq",masses[i],10,00);
        
        if options.createWorkspace:
            cur_hzz2l2v.createWorkspace();
            cur_hzz2l2t.createWorkspace();
            cur_hzz2l2q.createWorkspace();
            cur_hwwlvqq.createWorkspace();

        if options.runLimits:                        
            cur_hzz2l2v.runAsymLimit();
            cur_hzz2l2t.runAsymLimit();
            cur_hzz2l2q.runAsymLimit();
            cur_hwwlvqq.runAsymLimit();
                                
        cur_hzz2l2v.printLimts();
        cur_hzz2l2t.printLimts();
        cur_hzz2l2q.printLimts();
        cur_hwwlvqq.printLimts();
        
        EL_hzz2l2v_0s.append(cur_hzz2l2v.lims[3])
        EL_hzz2l2t_0s.append(cur_hzz2l2t.lims[3])
        EL_hzz2l2q_0s.append(cur_hzz2l2q.lims[3])
        EL_hwwlvqq_0s.append(cur_hwwlvqq.lims[3])
                                                        
        #print cur_hzz2l2v.lims 
        
    ## ---------------------------------------------------------        
    # make graphs
    gr_hzz2l2v = ROOT.TGraph(nMasses,masses_array,EL_hzz2l2v_0s);
    gr_hzz2l2t = ROOT.TGraph(nMasses,masses_array,EL_hzz2l2t_0s);
    gr_hzz2l2q = ROOT.TGraph(nMasses,masses_array,EL_hzz2l2q_0s);
    gr_hwwlvqq = ROOT.TGraph(nMasses,masses_array,EL_hwwlvqq_0s);            
    gr_hzz2l2v.SetLineColor(3);
    gr_hzz2l2t.SetLineColor(7);
    gr_hzz2l2q.SetLineColor(4);
    gr_hwwlvqq.SetLineColor(6); 
        
    # draw limits!
    leg = ROOT.TLegend(0.15,0.6,0.4,0.85);
    leg.SetFillStyle(1001);
    leg.SetFillColor(0);    
    leg.SetBorderSize(1);    
    leg.AddEntry(gr_hzz2l2v,"hzz2l2v","l");
    leg.AddEntry(gr_hzz2l2t,"hzz2l2t","l");
    leg.AddEntry(gr_hzz2l2q,"hzz2l2q","l");
    leg.AddEntry(gr_hwwlvqq,"hwwlvqq","l");
    
    oneLine = ROOT.TF1("oneLine","1",599,1001);
    oneLine.SetLineColor(ROOT.kRed);
    oneLine.SetLineWidth(1);

    can = ROOT.TCanvas("can","can",1200,800);
    hrl = can.DrawFrame(599,0.1,1001,100.);
    hrl.GetYaxis().SetTitle("#mu' = C' #times #mu");
    hrl.GetXaxis().SetTitle("mass (GeV)");
    can.SetGrid(); 
    gr_hzz2l2v.Draw();
    gr_hzz2l2t.Draw();
    gr_hzz2l2q.Draw();
    gr_hwwlvqq.Draw();
    oneLine.Draw("LSAMES");
    leg.Draw()
    ROOT.gPad.SetLogy();
    can.SaveAs("test.eps");
                   
                   
                   