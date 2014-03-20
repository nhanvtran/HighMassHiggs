import os
import glob
import math
import array
import sys
import time
import ROOT
        
##########################################################################################################

class chanWP:

    def __init__(self,abspath,channel,mass,cpsq,brnew):

        self.abspath = abspath;

        self.channel = channel;
        self.mass    = mass;
        self.cpsq    = cpsq;
        self.brnew   = brnew;
        
        self.opath   = "tmp/";
        self.lims    = [0,0,0,0,0,0];
        self.cwd = os.getcwd();
        self.dcnames = [];        

    ##########################################################################################################        
        
    def setOPath(self,path):
        self.opath = path;
    
    ##########################################################################################################
    
    def createWorkspace(self):
                
        # setup the path
        massdir = "%03i" % self.mass;
        bsmdir  = "cpsq%02i_brnew%02i" % (self.cpsq,self.brnew);
        localpath = self.channel + "/" + massdir + "/" + bsmdir + "/";
        
        # go to that dir
        os.chdir(self.abspath + "/" + localpath);

        # get the datacard names
        self.getDCNames();

        # combine cards for a given channel
        ccName = "combine_%s_%03i_%02i_%02i.txt" % (self.channel,self.mass,self.cpsq,self.brnew);
        combineCmmd = "combineCards.py ";
        for i in range(len(self.dcnames)): combineCmmd += " %s" % self.dcnames[i];
        combineCmmd += " > %s " % ccName;
        print combineCmmd
        os.system(combineCmmd);
        
        # turn into a workspace
        wsName = "/tmp/ws_%s_%03i_%02i_%02i.root" % (self.channel,self.mass,self.cpsq,self.brnew);
        cmmd = "text2workspace.py %s -o %s" % (ccName,self.cwd+wsName);
        print cmmd
        os.system(cmmd);
        
        # remove combined card
        os.remove(ccName);
        
        # come back
        os.chdir(self.cwd);

    ##########################################################################################################

    def runAsymLimit(self):
        
        os.chdir(self.opath);
        
        #combine ws_hzz2l2q_600_10_00.root -M Asymptotic -n "_nhantest" -m 600 -t -1
        ws = "ws_%s_%03i_%02i_%02i.root" % (self.channel,self.mass,self.cpsq,self.brnew);
        meth = "-M Asymptotic"
        oname = "_%s_%03i_%02i_%02i" % (self.channel,self.mass,self.cpsq,self.brnew);
        cmmd = "combine %s %s -n %s -m %03i -t -1" % (ws,meth,oname,self.mass);
        os.system(cmmd);

        os.chdir(self.cwd);
        
        self.getAsymLimits();

    ##########################################################################################################
    
    def getAsymLimits(self):
        
        file = "%s/higgsCombine_%s_%03i_%02i_%02i.Asymptotic.mH%03i.root" % (self.opath,self.channel,self.mass,self.cpsq,self.brnew,self.mass);
        
        f = ROOT.TFile(file);
        t = f.Get("limit");
        entries = t.GetEntries();
        
        for i in range(entries):
            
            t.GetEntry(i);
            t_quantileExpected = t.quantileExpected;
            t_limit = t.limit;
            
            #print "limit: ", t_limit, ", quantileExpected: ",t_quantileExpected;
            
            if t_quantileExpected == -1.: self.lims[0] = t_limit;
            elif t_quantileExpected >= 0.024 and t_quantileExpected <= 0.026: self.lims[1] = t_limit;
            elif t_quantileExpected >= 0.15 and t_quantileExpected <= 0.17: self.lims[2] = t_limit;            
            elif t_quantileExpected == 0.5: self.lims[3] = t_limit;            
            elif t_quantileExpected >= 0.83 and t_quantileExpected <= 0.85: self.lims[4] = t_limit;
            elif t_quantileExpected >= 0.974 and t_quantileExpected <= 0.976: self.lims[5] = t_limit;
            else: print "Unknown quantile!"

    ##########################################################################################################

    # will be different for a specific channel
    def getDCNames(self):

        # hzz2l2v
        if self.channel == "hzz2l2v":
            self.dcnames.append( "%s_%03i_8TeV_eeeq0jets.dat"    % ("hzz2l2v",self.mass) );
            self.dcnames.append( "%s_%03i_8TeV_eegeq1jets.dat"   % ("hzz2l2v",self.mass) );
            self.dcnames.append( "%s_%03i_8TeV_eevbf.dat"        % ("hzz2l2v",self.mass) );
            self.dcnames.append( "%s_%03i_8TeV_mumueq0jets.dat"  % ("hzz2l2v",self.mass) );
            self.dcnames.append( "%s_%03i_8TeV_mumugeq1jets.dat" % ("hzz2l2v",self.mass) );
            self.dcnames.append( "%s_%03i_8TeV_mumuvbf.dat"      % ("hzz2l2v",self.mass) );
            
        # hzz2l2t
        if self.channel == "hzz2l2t":        
            #self.dcnames.append( "DataCard_H%03i_2l2tau_PFIso_7TeV_LegacyPaper.txt"    % (self.mass) );
            self.dcnames.append( "DataCard_H%03i_2l2tau_PFIso_7TeV_8TeV_LegacyPaper.txt"    % (self.mass) );
            #self.dcnames.append( "DataCard_H%03i_2l2tau_PFIso_8TeV_LegacyPaper.txt"    % (self.mass) );                    
            
        # 4l  
        if self.channel == "hzz4l":        
            self.dcnames.append( "%s_2e2muS_7TeV_0.txt"          % ("hzz4l") );
            self.dcnames.append( "%s_2e2muS_7TeV_1.txt"          % ("hzz4l") );
            self.dcnames.append( "%s_4eS_7TeV_0.txt"             % ("hzz4l") );
            self.dcnames.append( "%s_4eS_7TeV_1.txt"             % ("hzz4l") );
            self.dcnames.append( "%s_4muS_7TeV_0.txt"            % ("hzz4l") );
            self.dcnames.append( "%s_4muS_7TeV_1.txt"            % ("hzz4l") );
                                                            
        # hzz2l2q
        if self.channel == "hzz2l2q":
            if self.mass <= 800: 
                self.dcnames.append( "%s_llallb_8TeV.txt"            % ("hzz2l2q") );
            self.dcnames.append( "%s_llallbMerged_8TeV.txt"      % ("hzz2l2q") );
            self.dcnames.append( "%s_VBF_8TeV.txt"               % ("hzz2l2q") );
                            
        # hwwlvqq
        if self.channel == "hwwlvqq":
            if self.mass >= 600: 
                self.dcnames.append( "%s_ggH%03i_em_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
                            

    ##########################################################################################################
    
    def printLimts(self,blind=True):
        
        self.getAsymLimits();
    
        init = 0;
        if blind: init = 1;
        print "channel: "
        for i in range(init,len(self.lims)):  
            print "lim ",i,":",round(self.lims[i],3);
    
