#! /usr/bin/env python

import os
import glob
import math
import array
import sys
import time
import ROOT
from array import array

from HMHUtilities import *

############################################
#            Job steering                  #
############################################
from optparse import OptionParser

parser = OptionParser()

parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
parser.add_option('--makeWorkingDirs',action="store_true",dest="makeWorkingDirs",default=False,help='do training')
parser.add_option('--runLimits',action="store_true",dest="runLimits",default=False,help='do training')
parser.add_option('--mkWkspace',action="store_true",dest="mkWkspace",default=False,help='do training')
parser.add_option('--isBatch',action="store_true",dest="isBatch",default=False,help='do training')
parser.add_option('--vbfOnly',action="store_true",dest="vbfOnly",default=False,help='do training')
parser.add_option('--ggfOnly',action="store_true",dest="ggfOnly",default=False,help='do training')
parser.add_option('--highMemory',action="store_true",dest="highMemory",default=False,help='do training')

parser.add_option('--mass',action="store",type="int",dest="mass",default=-1)
parser.add_option('--cpsq',action="store",type="int",dest="cpsq",default=-1)
parser.add_option('--brnew',action="store",type="int",dest="brnew",default=-1)
parser.add_option('--mlfit',action="store_true",dest="mlfit",default=False,help='do training')

(options, args) = parser.parse_args()

############################################################


#--------------------------------------------------

def makeWorkingDirs( svnpath, workdir, channels, mass, cpsq, brnew ):

    massdir = "%03i" % mass;
    bsmdir  = "cpsq%02i_brnew%02i" % (cpsq, brnew);
    bsmdirhzz = "cpsq10_brnew00";
    bsmdirhzz2 = "cpsq01_brnew00";

    curworkpath = workdir+"/"+"work_"+massdir+"_"+bsmdir;
    
    if os.path.exists(curworkpath):
        pass;
    else:
        os.makedirs(curworkpath)

    for i in range(len(channels)):
        localpath = channels[i] + "/" + massdir + "/" + bsmdir + "/";
        if "hzzllll" == channels[i] or "hzz4l" == channels[i]: localpath = channels[i] + "/" + massdir + "/" + bsmdirhzz + "/";
        svnDir = svnpath + "/" + localpath;
        print svnDir
        cpCmmd = "cp %s/*.* %s/." % (svnDir,curworkpath);
        os.system(cpCmmd);
        time.sleep(0.3);

        if "hzzllll" == channels[i] or "hzz4l" == channels[i]: 
            localpath2 = svnpath + "/" + channels[i] + "/" + massdir + "/" + bsmdirhzz2 + "/";
            cpCmmd2 = "cp %s/*.txt %s/." % (localpath2,curworkpath);
            os.system(cpCmmd2);
            time.sleep(0.3);   

    rmCmmd = "rm %s/out*" % (curworkpath);
    os.system(rmCmmd);
    time.sleep(0.5);
    #rmCmmd = "rm %s/condor*" % (curworkpath);
    #os.system(rmCmmd);    
    #time.sleep(0.5);

if __name__ == '__main__':

    ### ++++++++++++++++++++INPUTS+++++++++++++++++++ ###
    
    #svnpath = "/uscms_data/d2/ntran/physics/HighMassHiggs/svn/highmass2014"
    svnpath = "/uscms_data/d2/ntran/physics/HighMassHiggs/svn/cardlinks"
    
    workdir = "/uscms_data/d2/ntran/physics/HighMassHiggs/combine_052314/CMSSW_6_1_1/src/HighMassHiggs/tmpwork_082914/tmpwork"
    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_082914"
    #workdir = "/uscms_data/d2/ntran/physics/HighMassHiggs/combine_052314/CMSSW_6_1_1/src/HighMassHiggs/tmpwork_071614/tmpwork"
    #outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_071614"

    channels = ["hww2l2v","hwwlvqq","hzz2l2v","hzz2l2t","hzz2l2q","hzz4l"];
    #channels = ["hww2l2v","hwwlvqq","hzz2l2v","hzz2l2t","hzz2l2q"];
    #cpsq  = [01,02,03,05,07];
    cpsq  = [01,02,03,05,07,10];    
    brnew = [00,01,02,03,04,05];
    #brnew = [01,02,03,04,05];
    #mass  = [200,250,300,350,400,500,600,700,800,900,1000];
    #mass  = [400,500];
    mass  = [600,700];
    #mass  = [250,300,350,400,500,600,700,800,900,1000];
    #mass  = [145,150,160,170,180,190];#,200,250,300,350,400,500,600,700,800,900,1000];

    if options.cpsq  > 0: cpsq  = [options.cpsq];
    if options.brnew >= 0: brnew = [options.brnew];
    if options.mass  > 0: mass  = [options.mass];
    productionMode = 0;
    if options.ggfOnly: productionMode = 1;
    if options.vbfOnly: productionMode = 2;

    ctr = 0;
    for i in range(len(mass)):
        for j in range(len(cpsq)):
            for k in range(len(brnew)):
                gamFactor = (float(cpsq[j])/10.)/(1-(float(brnew[k])/10.));
                if gamFactor > 1: continue
                print mass[i],cpsq[j],brnew[k]

                channelsToRun = [];
                #channelsToRun.append( ["hww2l2v"] );
                #channelsToRun.append( ["hwwlvqq"] );
                #channelsToRun.append( ["hzz2l2v"] );
                #channelsToRun.append( ["hzz4l"] ); 
                #channelsToRun.append( ["hzz2l2t"] ); 
                #channelsToRun.append( ["hzz2l2q"] ); 
                ###channelsToRun.append( ["hww2l2v","hzz2l2v","hzz2l2q","hwwlvqq","hzz4l"] );                     
                channelsToRun.append( ["hww2l2v","hwwlvqq","hzz4l"] );  
                #channelsToRun.append( ["hww2l2v","hzz4l"] );  

    
                labels = ["comb_ww2l2v_wwlvqq_zz4l_TestE2A_p139"]
                #labels = ["hzz4l","hww2l2v","hwwlvqq"]
                #labels = ["hww2l2v","hwwlvqq","hzz4l","comb_ww2l2v_wwlvqq_zz4l"]
                #labels = ["hww2l2v"]

                if options.makeWorkingDirs:
                    makeWorkingDirs( svnpath, workdir, channels, mass[i], cpsq[j], brnew[k] );

                for aa in range(len(channelsToRun)):
                    testWP = singleWorkingPoint( labels[aa], workdir, outpath, channelsToRun[aa], mass[i], cpsq[j], brnew[k], productionMode, options.highMemory)
                    if options.mkWkspace: 
                        testWP.createWorkspace(options.isBatch,False);
                    if options.runLimits: 
                        method = "Asymptotic";
                        if options.mlfit: method = "MaxLikelihoodFit";
                        testWP.runAsymLimit(options.isBatch,method);
                    ctr += 1;

    print "ctr = ",ctr
 

