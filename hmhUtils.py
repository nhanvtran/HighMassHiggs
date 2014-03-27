import os
import glob
import math
import array
import sys
import time
import ROOT

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##### inherited class for holding the ws information
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################

class workspaceContainer:

    def __init__(self,wsName,eosLocation,olabel):

        self.cwd         = os.getcwd();
        self.wsName      = wsName;
        self.wsDir       = os.path.dirname(wsName);
        self.wsFN        = os.path.basename(wsName);       
        self.eosLocation = eosLocation;
        self.olabel      = olabel;
        self.lims        = [-1,-1,-1,-1,-1,-1];        

    def runAsymLimit(self, isBatch, mass, channel = "ALL"):
                
        os.chdir( self.wsDir );
        
        # combine options
        meth = "-M Asymptotic"        
        combineOptions = "--run expected";
        #if channel == "ALL": continue; 
        if channel == "hzz4l": 
            combineOptions += " --minosAlgo=stepping --X-rtd TMCSO_AdaptivePseudoAsimov --minimizerStrategy=0 --minimizerTolerance=0.0001 --cminFallback Minuit2:0.01 --cminFallback Minuit:0.001";
        #else: continue;
        
        cmmd = "combine %s %s -n %s -m %03i %s" % (self.wsFN,meth,self.olabel,mass,combineOptions);

        if isBatch: 
            self.submitBatchJobCombine(cmmd);
        else: 
            os.system(cmmd);

        os.chdir(self.cwd); 

    def submitBatchJobCombine(self, command):
            
        currentDir = os.getcwd();
        print "Submitting batch job from: ", currentDir

        fnCore = os.path.splitext(self.wsFN)[0];
        fn = "condorScript_%s" % (fnCore);
        
        # create a dummy bash/csh
        outScript=open(fn+".sh","w");
        
        outScript.write('#!/bin/bash');
        outScript.write("\n"+'date');
        outScript.write("\n"+'source /uscmst1/prod/sw/cms/bashrc prod');
        outScript.write("\n"+'cd '+self.wsDir);
        outScript.write("\n"+'eval `scram runtime -sh`');
        outScript.write("\n"+'cd -');
        outScript.write("\n"+'ls');    
        outScript.write("\n"+command);
        outScript.write("\n"+'cp higgsCombine*'+self.olabel+'*.root '+self.eosLocation);
        outScript.close();
        
        # link a condor script to your shell script
        condorScript=open("subCondor_"+fn,"w");
        condorScript.write('universe = vanilla')
        condorScript.write("\n"+"Executable = "+fn+".sh")
        condorScript.write("\n"+'Requirements = Memory >= 199 &&OpSys == "LINUX"&& (Arch != "DUMMY" )&& Disk > 1000000')
        condorScript.write("\n"+'Should_Transfer_Files = YES')
        condorScript.write("\n"+'Transfer_Input_Files = '+self.wsName)    
        condorScript.write("\n"+'WhenToTransferOutput  = ON_EXIT_OR_EVICT')
        condorScript.write("\n"+'Output = out_$(Cluster).stdout')
        condorScript.write("\n"+'Error  = out_$(Cluster).stderr')
        condorScript.write("\n"+'Error  = out_$(Cluster).stderr')
        condorScript.write("\n"+'Log    = out_$(Cluster).log')
        condorScript.write("\n"+'Notification    = Error')
        condorScript.write("\n"+'Queue 1')
        condorScript.close();
        
        # submit the condor job 
        
        os.system("condor_submit "+"subCondor_"+fn)

    def getAsymLimits(self):
                
        file = "%s/%s" % (self.eospath,self.outputName);
        
        if not os.path.isfile(file): 
            print "Warning (GetAsymLimits): "+file+" does not exist"
            return;
        
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
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
        
##########################################################################################################
# class for combining all the channels
##########################################################################################################

class combinedClass:
    
    def __init__(self,channelContainers,channel="ALL"):    
        
        self.chanWPs = channelContainers;        
        allChannels = [ self.chanWPs[i].channel for i in range(len(self.chanWPs)) ]
        print "Combining these channels: ", allChannels

        self.channel = channel;        
        self.mass    = self.chanWPs[0].mass;
        self.cpsq    = self.chanWPs[0].cpsq;
        self.brnew   = self.chanWPs[0].brnew;
        self.opath   = self.chanWPs[0].opath;
        self.eospath = self.chanWPs[0].eospath
        self.lims    = [-1,-1,-1,-1,-1,-1];
        self.cwd = os.getcwd();
                
        tmpdirname = "tmptmp_%03i_%02i_%02i" % (self.mass,self.cpsq,self.brnew);
        self.tmpdir = tmpdirname;
        
        if not os.path.exists(self.tmpdir):
            os.makedirs(self.tmpdir)
            
        for i in range(len(self.chanWPs)):
            cpCmmd = "cp %s/*.* %s/." % (self.chanWPs[i].svnDir,self.tmpdir);
            os.system(cpCmmd);
            
        # the name of the workspace
        wsName = "%s/ws_%s_%03i_%02i_%02i.root" % (self.opath,self.channel,self.mass,self.cpsq,self.brnew);
        self.wsname = wsName;
            
        # the name of the output from combine
        olabel = "_%s_%03i_%02i_%02i" % (self.channel,self.mass,self.cpsq,self.brnew);
        self.wsContainer = workspaceContainer( self.wsname, self.eospath, olabel );
            
    def createCombinedWorkspace(self):
            
        curdir = os.getcwd();
        os.chdir(self.tmpdir);
        
        # combine cards for a given channel
        ccName = "combine_%s_%03i_%02i_%02i.txt" % (self.channel,self.mass,self.cpsq,self.brnew);
        combineCmmd = "combineCards.py ";
        for i in range(len(self.chanWPs)): 
            for j in range(len(self.chanWPs[i].dcnames)): combineCmmd += " %s" % self.chanWPs[i].dcnames[j];
        combineCmmd += " > %s " % ccName;
        print combineCmmd
        os.system(combineCmmd);
        
        # turn into a workspace
        wsName = "%s/ws_%s_%03i_%02i_%02i.root" % (self.opath,self.channel,self.mass,self.cpsq,self.brnew);
        cmmd = "text2workspace.py %s -o %s" % (ccName,wsName);
        print cmmd
        os.system(cmmd);
        
        os.chdir(curdir);

    ##########################################################################################################

    def runAsymLimit(self, isBatch):

        self.wsContainer.runAsymLimit(isBatch,self.mass,self.channel);

    ##########################################################################################################
    
    def getAsymLimits(self):
        
        self.wsContainer.getAsymLimits();
        self.lims = workspaceContainer.lims;
        return self.lims
        
    ##########################################################################################################

                    
##########################################################################################################
# class for each channel
##########################################################################################################

class chanWP:

    def __init__(self,abspath,channel,mass,cpsq,brnew,opath,eospath):

        self.abspath = abspath;

        self.channel = channel;
        self.mass    = mass;
        self.cpsq    = cpsq;
        self.brnew   = brnew;
        
        self.opath   = opath;
        self.eospath = eospath;
        self.lims    = [-1,-1,-1,-1,-1,-1];
        self.cwd = os.getcwd();
        self.dcnames = [];   
        
        self.massdir = "%03i" % self.mass;
        self.bsmdir  = "cpsq%02i_brnew%02i" % (self.cpsq,self.brnew);
        self.localpath = self.channel + "/" + self.massdir + "/" + self.bsmdir + "/";
        self.svnDir = self.abspath + "/" + self.localpath;
        
        # get the datacard names
        self.getDCNames();         
        
        # the name of the workspace
        wsName = "%s/ws_%s_%03i_%02i_%02i.root" % (self.opath,self.channel,self.mass,self.cpsq,self.brnew);
        self.wsname = wsName;
        
        # the name of the output from combine
        olabel = "_%s_%03i_%02i_%02i" % (self.channel,self.mass,self.cpsq,self.brnew);
        self.wsContainer = workspaceContainer( self.wsname, self.eospath, olabel );
    
    ##########################################################################################################
    
    def createWorkspace(self):
           
        if len(self.dcnames) == 0: return;
        
        # go to that dir
        os.chdir(self.svnDir);

        # combine cards for a given channel
        ccName = "combine_%s_%03i_%02i_%02i.txt" % (self.channel,self.mass,self.cpsq,self.brnew);
        combineCmmd = "combineCards.py ";
        for i in range(len(self.dcnames)): combineCmmd += " %s" % self.dcnames[i];
        combineCmmd += " > %s " % ccName;
        print combineCmmd
        os.system(combineCmmd);
        
        # turn into a workspace
        cmmd = "text2workspace.py %s -o %s" % (ccName,self.wsname);
        print cmmd
        os.system(cmmd);
        
        # remove combined card
        os.remove(ccName);
        
        # come back
        os.chdir(self.cwd);

    ##########################################################################################################

    def runAsymLimit(self, isBatch):

        self.wsContainer.runAsymLimit(isBatch,self.mass,self.channel);

    ##########################################################################################################
    
    def getAsymLimits(self):
        
        self.wsContainer.getAsymLimits();
        self.lims = workspaceContainer.lims;
        return self.lims
        
    ##########################################################################################################

    # will be different for a specific channel
    def getDCNames(self):

        # hzz2l2v
        if self.channel == "hzz2l2v":
            if self.mass >= 200:         
                self.dcnames.append( "%s_%03i_8TeV_eeeq0jets.dat"    % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_eegeq1jets.dat"   % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_eevbf.dat"        % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_mumueq0jets.dat"  % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_mumugeq1jets.dat" % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_mumuvbf.dat"      % ("hzz2l2v",self.mass) );
            
        # hzz2l2t
        if self.channel == "hzz2l2t":        
            if self.mass >= 200:         
                #self.dcnames.append( "DataCard_H%03i_2l2tau_PFIso_7TeV_LegacyPaper.txt"    % (self.mass) );
                self.dcnames.append( "DataCard_H%03i_2l2tau_PFIso_7TeV_8TeV_LegacyPaper.txt"    % (self.mass) );
                #self.dcnames.append( "DataCard_H%03i_2l2tau_PFIso_8TeV_LegacyPaper.txt"    % (self.mass) );                    
            
        # 4l  
        if self.channel == "hzz4l":        
            self.dcnames.append( "comb_%s.txt"                   % ("hzz4l") );
                                                            
        # hzz2l2q
        if self.channel == "hzz2l2q":
            if self.mass >= 230:
                self.dcnames.append( "%s_VBF_8TeV.txt"               % ("hzz2l2q") );            
                if self.mass >= 400: self.dcnames.append( "%s_llallbMerged_8TeV.txt"      % ("hzz2l2q") );
                if self.mass <= 800: self.dcnames.append( "%s_llallb_8TeV.txt"            % ("hzz2l2q") );
                            
        # hwwlvqq
        if self.channel == "hwwlvqq":
            if self.mass >= 600: 
                self.dcnames.append( "%s_ggH%03i_em_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
                self.dcnames.append( "%s_ggH%03i_em_2jet_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
            if self.mass >= 170 and self.mass < 600:
                self.dcnames.append( "hwwlvjj_shape_8TeV.txt" );
            
        # hww2l2v
        if self.channel == "hww2l2v":
            if self.mass <= 600:
                self.dcnames.append("hwwof_0j_shape_7TeV_SM.txt"); 
                self.dcnames.append("hwwof_1j_shape_7TeV_SM.txt"); 
                self.dcnames.append("hwwof_2j_shape_7TeV_SM.txt"); 
                self.dcnames.append("hwwsf_0j_cut_7TeV_SM.txt"); 
                self.dcnames.append("hwwsf_1j_cut_7TeV_SM.txt"); 
                self.dcnames.append("hwwsf_2j_cut_7TeV_SM.txt"); 
            self.dcnames.append("hwwof_0j_shape_8TeV_SM.txt"); 
            self.dcnames.append("hwwof_1j_shape_8TeV_SM.txt");                         
            self.dcnames.append("hwwof_2j_shape_8TeV_SM.txt");                                                                 
            self.dcnames.append("hwwsf_0j_cut_8TeV_SM.txt"); 
            self.dcnames.append("hwwsf_1j_cut_8TeV_SM.txt");                         
            self.dcnames.append("hwwsf_2j_cut_8TeV_SM.txt");                                                                 
        
        # check that the cards exist!!
        for i in range(len(self.dcnames)):
            if not os.path.isfile(self.svnDir+"/"+self.dcnames[i]): 
                print "warning, Missing DC at "+self.svnDir+"/"+self.dcnames[i]
                #raise Warning( "Missing DC at "+fullpath+"/"+self.dcnames[i] )
        
    