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

parser.add_option('--mass',action="store",type="int",dest="mass",default=10)
parser.add_option('--cpsq',action="store",type="int",dest="cpsq",default=10)
parser.add_option('--brnew',action="store",type="int",dest="brnew",default=00)

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
        cpCmmd = "cp %s/*.* %s/." % (svnDir,curworkpath);
        os.system(cpCmmd);

if __name__ == '__main__':

    ### ++++++++++++++++++++INPUTS+++++++++++++++++++ ###
    
    svnpath = "/uscms_data/d2/ntran/physics/HighMassHiggs/svn/highmass2014"
    workdir = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_052214/tmpwork"
    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_052214/outputs"

    channels = ["hww2l2v","hwwlvqq","hzz2l2v"];#,"hzz2l2q","hzz2l2t","hzz4l"];
    cpsq  = [01,02,03,05,07,10];
    #cpsq  = [01,02,03,05,07];    
    brnew = [00,01,02,03,04,05];
    mass  = [200,300,400,500,600,700,800,900,1000];

    cpsq = [options.cpsq];
    brnew = [options.brnew];
    mass = [options.mass];

    ctr = 0;
    for i in range(len(mass)):
        for j in range(len(cpsq)):
            for k in range(len(brnew)):
                gamFactor = (float(cpsq[j])/10.)/(1-(float(brnew[k])/10.));
                if gamFactor > 1: continue
                print mass[i],cpsq[j],brnew[k]

                if options.makeWorkingDirs:
                    makeWorkingDirs( svnpath, workdir, channels, mass[i], cpsq[j], brnew[k] );

                channelsToRun = [];
                #channelsToRun.append( ["hww2l2v"] );
                #channelsToRun.append( ["hwwlvqq"] );
                #channelsToRun.append( ["hzz2l2v"] );
                channelsToRun.append( ["hww2l2v","hwwlvqq","hzz2l2v"] );  
                #labels = ["hww2l2v","hwwlvqq","hzz2l2v","ww2l2v+wwlvqq+zz2l2v"]
                labels = ["ww2l2v+wwlvqq+zz2l2v"]
                #labels = ["hwwlvqq"];
                for aa in range(len(channelsToRun)):
                    testWP = singleWorkingPoint( labels[aa], workdir, outpath, channelsToRun[aa], mass[i], cpsq[j], brnew[k])
                    if options.mkWkspace: testWP.createWorkspace(options.isBatch);
                    if options.runLimits: testWP.runAsymLimit(options.isBatch);
                    ctr += 1;

    print "ctr = ",ctr
 

