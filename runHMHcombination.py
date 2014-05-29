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

parser.add_option('--mass',action="store",type="int",dest="mass",default=-1)
parser.add_option('--cpsq',action="store",type="int",dest="cpsq",default=-1)
parser.add_option('--brnew',action="store",type="int",dest="brnew",default=-1)

(options, args) = parser.parse_args()

############################################################


#--------------------------------------------------

def makeWorkingDirs( svnpath, workdir, channels, mass, cpsq, brnew ):

    massdir = "%03i" % mass;
    bsmdir  = "cpsq%02i_brnew%02i" % (cpsq, brnew);

    curworkpath = workdir+"/"+"work_"+massdir+"_"+bsmdir;
    
    if os.path.exists(curworkpath):
        pass;
    else:
        os.makedirs(curworkpath)

        for i in range(len(channels)):
            localpath = channels[i] + "/" + massdir + "/" + bsmdir + "/";
            svnDir = svnpath + "/" + localpath;
            print svnDir
            cpCmmd = "cp %s/*.* %s/." % (svnDir,curworkpath);
            os.system(cpCmmd);
            time.sleep(0.5);
        
        rmCmmd = "rm %s/out*" % (curworkpath);
        os.system(rmCmmd);
        time.sleep(0.5);
        rmCmmd = "rm %s/condor*" % (curworkpath);
        os.system(rmCmmd);    
        time.sleep(0.5);

if __name__ == '__main__':

    ### ++++++++++++++++++++INPUTS+++++++++++++++++++ ###
    
    svnpath = "/uscms_data/d2/ntran/physics/HighMassHiggs/svn/highmass2014"
    #workdir = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_052614/tmpwork"
    workdir = "/uscms_data/d2/ntran/physics/HighMassHiggs/combine_052314/CMSSW_6_1_1/src/HighMassHiggs/tmpwork_052814/tmpwork"
    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_052814"

    channels = ["hww2l2v","hwwlvqq","hzz2l2v","hzzllll","hzz2l2t","hzz2l2q"];
    #channels = ["hzzllll"];#,"hzz2l2q","hzz2l2t","hzz4l"];    
    #cpsq  = [01,02,03,05,07,10];
    cpsq  = [01,02,03,05,07,10];    
    brnew = [01,02,03,04,05];
    mass  = [200,250,300,350,400,500,600,700,800,900,1000];
    #mass  = [200,230,250,270,300,350,400,440,500,540,600,700,800,900,1000];

    if options.cpsq  > 0: cpsq  = [options.cpsq];
    if options.brnew >= 0: brnew = [options.brnew];
    if options.mass  > 0: mass  = [options.mass];

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
                #channelsToRun.append( ["hzzllll"] ); 
                #channelsToRun.append( ["hzz2l2t"] ); 
                #channelsToRun.append( ["hzz2l2q"] ); 
                channelsToRun.append( ["hww2l2v","hwwlvqq","hzz2l2v","hzz2l2t","hzz2l2q","hzzllll"] );  
                #labels = ["hww2l2v","hwwlvqq","hzz2l2v","hzzllll","hzz2l2t","hzz2l2q","combined"]
                #labels = ["hzz2l2q","combined"]
                labels = ["combined"]
                #labels = ["hwwlvqq"];
                #labels = ["comb_5"];

                if options.makeWorkingDirs:
                    makeWorkingDirs( svnpath, workdir, channels, mass[i], cpsq[j], brnew[k] );

                for aa in range(len(channelsToRun)):
                    testWP = singleWorkingPoint( labels[aa], workdir, outpath, channelsToRun[aa], mass[i], cpsq[j], brnew[k])
                    if options.mkWkspace: 
                        testWP.createWorkspace(options.isBatch,False);
                    if options.runLimits: testWP.runAsymLimit(options.isBatch);
                    ctr += 1;

    print "ctr = ",ctr
 

