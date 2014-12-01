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
        #if "hzzllll" == channels[i] or "hzz4l" == channels[i] and cpsq < 10: localpath = channels[i] + "/" + massdir + "/" + bsmdirhzz2 + "/";
        svnDir = svnpath + "/" + localpath;                
        if (cpsq == 00) and channels[i] != "hzz4l": svnDir  = svnpath + "/" + channels[i] + "/" + massdir + "/" + "cpsq001_brnew%02i" % (brnew);
        if (cpsq == 50) and channels[i] != "hzz4l": svnDir  = svnpath + "/" + channels[i] + "/" + massdir + "/" + "cpsq001_brnew%02i" % (brnew);
        if (cpsq == 30) and channels[i] != "hzz4l": svnDir  = svnpath + "/" + channels[i] + "/" + massdir + "/" + "cpsq001_brnew%02i" % (brnew);
        if (cpsq == 00) and channels[i] != "hwwlvqq" and mass >= 600: svnDir  = svnpath + "/" + channels[i] + "/" + massdir + "/" + "cpsq001_brnew%02i" % (brnew);
        if (cpsq == 50) and channels[i] != "hwwlvqq" and mass >= 600: svnDir  = svnpath + "/" + channels[i] + "/" + massdir + "/" + "cpsq005_brnew%02i" % (brnew);
        if (cpsq == 30) and channels[i] != "hwwlvqq" and mass >= 600: svnDir  = svnpath + "/" + channels[i] + "/" + massdir + "/" + "cpsq003_brnew%02i" % (brnew);

        print "svnDir = ", svnDir
        cpCmmd = "cp %s/*.* %s/." % (svnDir,curworkpath);
        os.system(cpCmmd);
        time.sleep(0.2);

        if "hzzllll" == channels[i] or "hzz4l" == channels[i] and cpsq == 10: 
            localpath2 = svnpath + "/" + channels[i] + "/" + massdir + "/" + bsmdirhzz + "/";
            cpCmmd2 = "cp %s/*.txt %s/." % (localpath2,curworkpath);
            os.system(cpCmmd2);
            time.sleep(0.3);   
        if "hzzllll" == channels[i] or "hzz4l" == channels[i] and cpsq < 10: 
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
    
    workdir = "/uscms_data/d2/ntran/physics/HighMassHiggs/combine_100814/CMSSW_6_1_1/src/HighMassHiggs/tmpwork_102614/tmpwork"
    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_102614"
    #workdir = "/uscms_data/d2/ntran/physics/HighMassHiggs/combine_052314/CMSSW_6_1_1/src/HighMassHiggs/tmpwork_071614/tmpwork"
    #outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_071614"

    channels = ["hww2l2v","hwwlvqq","hzz2l2v","hzz2l2t","hzz2l2q","hzz4l"];
    #channels = ["hww2l2v","hwwlvqq","hzz2l2v","hzz2l2t","hzz2l2q"];
    cpsq  = [01,02,03,05,07];
    ##cpsq  = [01,02,03,05,07,10];    
    ###cpsq  = [02,03,05];    
    brnew = [00,01,02,03,04,05];
    #brnew = [01,02,03,04,05];
    #mass  = [600,700,800,900,1000];
    #mass  = [400,500];
    #mass  = [600,700];
    #mass  = [250,300,350,400,500,600,700,800,900,1000];
    #mass  = [200,250,300,350,400,500,600,700,800,900,1000];
    mass  = [145,150,160,170,180,190,200,250,300,350,400,500,600,700,800,900,1000];
    #mass  = [145,150,160,170,180,190];

    if options.cpsq  > -1: cpsq  = [options.cpsq];
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
                if gamFactor > 1 and cpsq < 20: continue
                print mass[i],cpsq[j],brnew[k]

                ## ------------------------
                channelsToRun = [];
                channelsToRun.append( ["hww2l2v","hzz2l2v","hzz2l2q","hwwlvqq","hzz4l"] );                     
                #labels = ["combined_BSM"]
                labels = ["combined_BSM_ggF"]
                # labels = ["combined_BSM_vbf"]

                #channelsToRun.append( ["hww2l2v","hwwlvqq"] );                     
                #channelsToRun.append( ["hzz2l2v","hzz2l2q","hzz4l"] );                     
                #labels = ["combined_WW_SM"]
                #labels = ["combined_ZZ_SM"]
                ## ------------------------

                #channelsToRun.append( ["hww2l2v"] );
                #channelsToRun.append( ["hwwlvqq"] );
                #channelsToRun.append( ["hzz2l2v"] );
                #channelsToRun.append( ["hzz4l"] ); 
                #channelsToRun.append( ["hzz2l2t"] ); 
                #channelsToRun.append( ["hzz2l2q"] ); 
                #channelsToRun.append( ["hww2l2v","hwwlvqq"] );                     
                #channelsToRun.append( ["hzz2l2v","hzz2l2q","hzz4l"] );                     
                #channelsToRun.append( ["hww2l2v","hzz2l2v","hzz2l2q","hwwlvqq","hzz4l"] );                     
                #channelsToRun.append( ["hww2l2v","hwwlvqq","hzz4l"] );  
                #channelsToRun.append( ["hww2l2v","hzz4l"] );  

    
                #labels = ["hzz4l_4muS_4eS_noPSA_t0"]
                #labels = ["comb_wwlvlv_wwlvqq_hzz4l_allSys"]
                ##labels = ["comb_zz4l_reduced3b"]
                ###labels = ["comb_wwlvqq_order3"]
                #labels = ["hww2l2v_v0","hwwlvqq_v0","hzz4l_v0","comb_allNo2l2t_v0"]
                
                #labels = ["hww2l2v","hwwlvqq","hzz2l2v","hzz4l","hzz2l2t","hzz2l2q","combined_all"]
                #labels = ["combined_BSM_ggF"]
                #labels = ["combined_SM_prodv2"];
                #labels = ["combined_WW_SM","combined_ZZ_SM"]
                #labels = ["combined_WW_SM"]
                #labels = ["hww2l2v_ewk"];#,"combined_WW_SM","combined_ZZ_SM","combined_SM"]
                #labels = ["hww2l2v","hwwlvqq","hzz2l2v","hzz2l2t","hzz2l2q"]


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
 

