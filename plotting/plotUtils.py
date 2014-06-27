import os
import glob
import math
import array
import sys
import time
import ROOT


## ===========================================================================================

def getAsymLimits(outpath,label,mass, cpsq, brnew,postfix=""):

    outputName = "higgsCombine_%s_%03i_%02i_%02i%s.Asymptotic.mH%03i.root" % (label,mass,cpsq,brnew,postfix,mass);
    file = "%s/%s" % (outpath,outputName);
    print file
    lims = [0]*6;
    
    if not os.path.isfile(file): 
        print "Warning (GetAsymLimits): "+file+" does not exist"
        return lims;

    f = ROOT.TFile(file);
    t = f.Get("limit");

    #if not t.GetListOfKeys().Contains("limit"): 
    if not t: 
        print "file is corrupted";
        return lims

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


def getMultiDimLimits(outpath,label,postfix,mass, cpsq, brnew):

    outputName = "higgsCombine_%s_%03i_%02i_%02i%s.MultiDimFit.mH%03i.root" % (label,mass,cpsq,brnew,postfix,mass);
    file = "%s/%s" % (outpath,outputName);
    f = ROOT.TFile(file);
    print file

    if not os.path.isfile(file): 
        print "Warning (GetAsymLimits): "+file+" does not exist"
        return 0;

    t = f.Get("limit");
    entries = t.GetEntries();
    
    x_a = array.array('d', []);
    y_a = array.array('d', []);

    mode = postfix.replace('_','');

    # timesLargerThan2Sigma = 0;
    # isAbove = False;
    # for i in range(entries):

    #     t.GetEntry(i);
    #     curr = getattr(t,"r"+postfix);
    #     curnll = getattr(t, "deltaNLL");

    #     if curnll > 3.96 and isAbove == False:
    #         timesLargerThan2Sigma += 1;
    #         isAbove = True;
    #         if timesLargerThan2Sigma > 1: break;
    #         y_a.append( getattr(t,"r"+postfix) );
    #         x_a.append( getattr(t, "deltaNLL") );
    #     elif curnll > 3.96 and isAbove == True: 
    #         if timesLargerThan2Sigma > 1: break;           
    #         y_a.append( getattr(t,"r"+postfix) );
    #         x_a.append( getattr(t, "deltaNLL") );
    #     elif curnll < 3.96 and isAbove == True:            
    #         if timesLargerThan2Sigma > 1: break;            
    #         y_a.append( getattr(t,"r"+postfix) );
    #         x_a.append( getattr(t, "deltaNLL") );
    #         isAbove = False;
    #     elif curnll < 3.96 and isAbove == False:            
    #         if timesLargerThan2Sigma > 1: break;            
    #         y_a.append( getattr(t,"r"+postfix) );
    #         x_a.append( getattr(t, "deltaNLL") );
    #     else: print "there are no other options!"

    #     print "timesLargerThan2Sigma = ", timesLargerThan2Sigma, curr, curnll;

    prevr   = 99999.;
    prevnll = 99999.;
    crossings = [];

    the_r   = 99999.;

    #print "entries = ",entries;
    for i in range(1,entries):

        t.GetEntry(i);
        curr = getattr(t,"r"+postfix);
        curnll = getattr(t, "deltaNLL");

        if i > 0:
            #print i,curr,curnll
            if (curnll > 3.96 and prevnll < 3.96) and curr < 1000:
                crossings.append( curr );
            if (curnll < 3.96 and prevnll > 3.96) and prevr < 1000:    
                crossings.append( prevr );
            #     print i,curr,curnll
            #     print prevr,prevnll

            #     x_a = array.array('d', []);
            #     y_a = array.array('d', []);

            #     x_a.append(prevnll); x_a.append(curnll);
            #     y_a.append(prevr  ); y_a.append(curr);
            #     graph = ROOT.TGraph(len(x_a),x_a,y_a);
            #     val = graph.Eval(3.96);
            #     if val < the_r: 
            #         the_r = val;
            #         break;

        prevnll = curnll;
        prevr   = curr;

    print crossings
    if len(crossings) > 0: the_r = max(crossings);
    else: the_r = 1000;

    print "the_r = ",the_r
    return the_r;

def getMultiDimLimitsOne(outputName,postfix):

    #outputName = filename;
    file = outputName;
    f = ROOT.TFile(outputName);
    print file

    if not os.path.isfile(file): 
        print "Warning (GetAsymLimits): "+file+" does not exist"
        return 0;

    t = f.Get("limit");
    entries = t.GetEntries();
    
    x_a = array.array('d', []);
    y_a = array.array('d', []);

    #mode = postfix.replace('_','');

    prevr   = 99999.;
    prevnll = 99999.;
    crossings = [];

    the_r   = 99999.;

    #print "entries = ",entries;
    for i in range(1,entries):

        t.GetEntry(i);
        curr = getattr(t,"r"+postfix);
        curnll = getattr(t, "deltaNLL");

        if i > 0:
            #print i,curr,curnll
            if (curnll > 3.96 and prevnll < 3.96) and curr < 1000:
                crossings.append( curr );
            if (curnll < 3.96 and prevnll > 3.96) and prevr < 1000:    
                crossings.append( prevr );
            #     print i,curr,curnll
            #     print prevr,prevnll

            #     x_a = array.array('d', []);
            #     y_a = array.array('d', []);

            #     x_a.append(prevnll); x_a.append(curnll);
            #     y_a.append(prevr  ); y_a.append(curr);
            #     graph = ROOT.TGraph(len(x_a),x_a,y_a);
            #     val = graph.Eval(3.96);
            #     if val < the_r: 
            #         the_r = val;
            #         break;

        prevnll = curnll;
        prevr   = curr;

    print crossings
    if len(crossings) > 0: the_r = max(crossings);
    else: the_r = 1000;

    print "the_r = ",the_r
    return the_r;







