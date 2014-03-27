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
parser.add_option('--getLimits',action="store_true",dest="getLimits",default=False,help='do training')

(options, args) = parser.parse_args()

############################################################

#--------------------------------------------------

if __name__ == '__main__':

    ### +++++++++++++++++++++++++++++++++++++++++++++ ###
    ### ++++++++++++++++++++INPUTS+++++++++++++++++++ ###
    
    abspath = "/uscms_data/d2/ntran/physics/HighMassHiggs/svn/highmass2014"
    tmpdir  = "/uscms_data/d2/ntran/physics/HighMassHiggs/CMSSW_6_1_1/src/HighMassHiggs/tmp3"
    eosPath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/test3"

    # for some reason XXX is causing the full combination to break...
    # submitted hzz4l to it's own dir

    masses = [200,300,400,500,600,700,800,900,1000];
    #masses = [400];    
#    masses = [145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,
#            165,170,175,180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,
#            255,260,265,270,275,280,285,290,295,300,
#            310,320,330,340,350,360,370,380,390,400,420,440,460,480,500,520,540,560,580,
#            600,700,800,900,1000];

    nMasses       = len(masses);

    arrays_masses = []
    arrays_0sigma = [];
    
    useBatch = True;

    #channels = ["hzz2l2q","hwwlvqq","hww2l2v","hzz2l2v"];
    #channels = ["hzz2l2t"];
    channels = ["hzz2l2q","hwwlvqq","hww2l2v","hzz2l2v","hzz2l2t"]
    #channels = ["hzz4l"];
    
    ### +++++++++++++++++++++++++++++++++++++++++++++ ###
    ### +++++++++++++++++++++++++++++++++++++++++++++ ###
    
    for a in range(len(channels)):
        arrays_masses.append( array.array('d', []) );
        arrays_0sigma.append( array.array('d', []) );
    # for combination
    arrays_masses.append( array.array('d', []) );
    arrays_0sigma.append( array.array('d', []) );
                                                    
    for i in range(len(masses)):
        
        # --------------
        # each channel container
        chanContainers = [];
        for a in range(len(channels)):
            chanContainers.append( chanWP(abspath,channels[a],masses[i],10,00) );
        # --------------

        for a in range(len(chanContainers)):       
            chanContainers[a].setOPath(tmpdir)
            chanContainers[a].setEosPath(eosPath)
                
#        if options.createWorkspace:
#            for a in range(len(chanContainers)):       
#                chanContainers[a].createWorkspace();
#        
#        if options.runLimits:                        
#            for a in range(len(chanContainers)):       
#                chanContainers[a].runAsymLimit(useBatch);

        if options.getLimits:
            for a in range(len(chanContainers)): 
                chanContainers[a].getAsymLimits();
                if chanContainers[a].lims[3] > 0: 
                    print "mass = ", masses[i], ", and channel = ", channels[a]
                    arrays_masses[a].append( masses[i] );
                    arrays_0sigma[a].append( chanContainers[a].lims[3] );
                    
        combiner = combinedClass( chanContainers );
        combiner.setOPath(tmpdir)
        combiner.setEosPath(eosPath)
        if options.createWorkspace:
            combiner.createCombinedWorkspace();
        if options.runLimits:                                
            combiner.runAsymLimit(useBatch);
        if options.getLimits:
            combiner.getAsymLimits();  
            if combiner.lims[3] > 0: 
                arrays_masses[len(channels)].append( masses[i] );
                arrays_0sigma[len(channels)].append( combiner.lims[3] );

  
    ## ---------------------------------------------------------        
    
    if options.getLimits:

        channels.append("ALL");

        # make graphs
        graphs = [];
        for a in range(len(channels)):
            print "len(arrays_masses[a]) = ", len(arrays_masses[a])
            graphs.append( ROOT.TGraph( len(arrays_masses[a]), arrays_masses[a], arrays_0sigma[a] ) );

        # draw limits!
        colors = [2,4,6,7,3,1];
        widths = [2,2,2,2,2,3];        
        leg = ROOT.TLegend(0.15,0.6,0.4,0.85);
        leg.SetFillStyle(1001);
        leg.SetFillColor(0);    
        leg.SetBorderSize(1);  
        for a in range(len(channels)):
            graphs[a].SetLineColor( colors[a] );        
            graphs[a].SetLineWidth( widths[a] );                    
            leg.AddEntry(graphs[a],channels[a],"l");
            
        oneLine = ROOT.TF1("oneLine","1",199,1001);
        oneLine.SetLineColor(ROOT.kRed+2);
        oneLine.SetLineWidth(1);
        oneLine.SetLineStyle(2);
                 
        can = ROOT.TCanvas("can","can",1200,800);
        hrl = can.DrawFrame(199,0.1,1001,100.);
        hrl.GetYaxis().SetTitle("#sigma_{95CL}/#sigma_{SM}");
        hrl.GetXaxis().SetTitle("mass (GeV)");
        can.SetGrid(); 

        for a in range(len(channels)): graphs[a].Draw();

        oneLine.Draw("LSAMES");
        leg.Draw()
        ROOT.gPad.SetLogy();
        can.SaveAs("test.eps");        
                                 
                   
                   