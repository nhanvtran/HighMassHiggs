import os
import glob
import math
import array
import sys
import time
import ROOT


## ===========================================================================================

def getAsymLimits(outpath,label,mass, cpsq, brnew):

    outputName = "higgsCombine_%s_%03i_%02i_%02i.Asymptotic.mH%03i.root" % (label,mass,cpsq,brnew,mass);
    file = "%s/%s" % (outpath,outputName);
    print file
    lims = [0]*6;
    
    if not os.path.isfile(file): 
        print "Warning (GetAsymLimits): "+file+" does not exist"
        return lims;

    f = ROOT.TFile(file);
    t = f.Get("limit");
    entries = t.GetEntries();

    for i in range(entries):

        t.GetEntry(i);
        t_quantileExpected = t.quantileExpected;
        t_limit = t.limit;

        #print "limit: ", t_limit, ", quantileExpected: ",t_quantileExpected;
        
        if t_quantileExpected == -1.: lims[0] = t_limit;
        elif t_quantileExpected >= 0.024 and t_quantileExpected <= 0.026: lims[1] = t_limit;
        elif t_quantileExpected >= 0.15 and t_quantileExpected <= 0.17: lims[2] = t_limit;            
        elif t_quantileExpected == 0.5: lims[3] = t_limit;            
        elif t_quantileExpected >= 0.83 and t_quantileExpected <= 0.85: lims[4] = t_limit;
        elif t_quantileExpected >= 0.974 and t_quantileExpected <= 0.976: lims[5] = t_limit;
        else: print "Unknown quantile!"

    return lims;

