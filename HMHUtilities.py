import os
import glob
import math
import array
import sys
import time
import ROOT


class singleWorkingPoint:

    def __init__(self, label, workpath, outpath, channels, mass, cpsq, brnew):

    	self.label    = label;
        self.workpath = workpath;
        self.outpath  = outpath;
        self.cwd      = os.getcwd();

        self.channels = channels;
        self.mass     = mass;
        self.cpsq     = cpsq;
        self.brnew    = brnew;

        massdir = "%03i" % mass;
        bsmdir  = "cpsq%02i_brnew%02i" % (cpsq, brnew);
        self.curworkpath = self.workpath+"/work_"+massdir+"_"+bsmdir;1
        
        self.dcnames  = [];
        self.getDCNames();

        self.wsName = "ws_%s_%03i_%02i_%02i.root" % (self.label,self.mass,self.cpsq,self.brnew);

	##########################################################################################################

    def createWorkspace(self, isBatch):
           
        if len(self.dcnames) == 0: return;
        
        # go to that dir
        os.chdir(self.curworkpath);

        # combine cards for a given channel
        ccName = "combine_%s_%03i_%02i_%02i.txt" % (self.label,self.mass,self.cpsq,self.brnew);
        combineCmmd = "combineCards.py ";
        for i in range(len(self.dcnames)): 
            self.hardFix1(self.dcnames[i]);
            combineCmmd += " %s" % self.dcnames[i];
        combineCmmd += " > %s " % ccName;
        #print combineCmmd
        #os.system(combineCmmd);
        
        # turn into a workspace
        cmmd = "text2workspace.py %s -o %s" % (ccName,self.wsName);
        #if not isBatch: cmmd += " &";
        
        # remove combined card
        #os.remove(ccName);
        
        if isBatch:
            self.submitBatchJobMakeWS(combineCmmd,cmmd,self.curworkpath,self.wsName);

        else:
            # print "combineCmmd: ", combineCmmd
            # print "cmmd: ", cmmd            
            os.system(combineCmmd);
            time.sleep(1.);
            os.system(cmmd);

        
        # come back
        os.chdir(self.cwd);

    ##########################################################################################################

    def runAsymLimit(self, isBatch):
        
        os.chdir( self.curworkpath );

        # combine options
        meth = "-M Asymptotic"        
        combineOptions = "--run expected";
        #if channel == "ALL": continue; 
        if "hzz4l" in self.channels: 
            combineOptions += " --minosAlgo=stepping --X-rtd TMCSO_AdaptivePseudoAsimov --minimizerStrategy=0 --minimizerTolerance=0.0001 --cminFallback Minuit2:0.01 --cminFallback Minuit:0.001";
        #else: continue;
        
        biglabel = "_%s_%03i_%02i_%02i" % (self.label,self.mass,self.cpsq,self.brnew);

        cmmd = "combine %s %s -n %s -m %03i %s" % (self.wsName,meth,biglabel,self.mass,combineOptions);
        print cmmd
        

        if isBatch: 
            self.submitBatchJobCombine(cmmd);
        else: 
            os.system(cmmd);
            os.system('mv higgsCombine*'+biglabel+'*.root '+self.outpath)

        os.chdir(self.cwd); 

    def submitBatchJobCombine(self, command):
            
        currentDir = os.getcwd();
        print "Submitting batch job from: ", currentDir

        fnCore = os.path.splitext(self.wsName)[0];
        fn = "condorScript_%s" % (fnCore);
        
        # create a dummy bash/csh
        outScript=open(fn+".sh","w");
        
        outScript.write('#!/bin/bash');
        outScript.write("\n"+'date');
        outScript.write("\n"+'source /uscmst1/prod/sw/cms/bashrc prod');
        outScript.write("\n"+'cd '+self.cwd);
        outScript.write("\n"+'eval `scram runtime -sh`');
        outScript.write("\n"+'cd -');
        outScript.write("\n"+'ls');    
        outScript.write("\n"+command);
        outScript.write("\n"+'cp higgsCombine*'+self.label+'*.root '+self.outpath);
        outScript.close();
        
        # link a condor script to your shell script
        condorScript=open("subCondor_"+fn,"w");
        condorScript.write('universe = vanilla')
        condorScript.write("\n"+"Executable = "+fn+".sh")
        condorScript.write("\n"+'Requirements = Memory >= 199 &&OpSys == "LINUX"&& (Arch != "DUMMY" )&& Disk > 1000000')
        condorScript.write("\n"+'Should_Transfer_Files = YES')
        condorScript.write("\n"+'Transfer_Input_Files = '+self.wsName)    
        condorScript.write("\n"+'WhenToTransferOutput  = ON_EXIT_OR_EVICT')
        condorScript.write("\n"+'Output = out'+self.label+'_$(Cluster).stdout')
        condorScript.write("\n"+'Error  = out'+self.label+'_$(Cluster).stderr')
        condorScript.write("\n"+'Log    = out'+self.label+'_$(Cluster).log')
        condorScript.write("\n"+'Notification    = Error')
        condorScript.write("\n"+'Queue 1')
        condorScript.close();
        
        # submit the condor job 
        
        os.system("condor_submit "+"subCondor_"+fn)        

	##########################################################################################################
	##########################################################################################################
    ##########################################################################################################

    # will be different for a specific channel
    def getDCNames(self):

        # hzz2l2v
        if "hzz2l2v" in self.channels:
            if self.mass >= 200:         
                self.dcnames.append( "%s_%03i_8TeV_eeeq0jets.dat"    % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_eegeq1jets.dat"   % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_eevbf.dat"        % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_mumueq0jets.dat"  % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_mumugeq1jets.dat" % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_mumuvbf.dat"      % ("hzz2l2v",self.mass) );
            
        # hzz2l2t
        if "hzz2l2t" in self.channels:       
            if self.mass >= 200:         
                self.dcnames.append( "DataCard_2l2tau_PFIso_7TeV_LegacyPaper.txt" );
                self.dcnames.append( "DataCard_2l2tau_PFIso_8TeV_LegacyPaper.txt" );
                #self.dcnames.append( "DataCard_H%03i_2l2tau_PFIso_7TeV_8TeV_LegacyPaper.txt"    % (self.mass) );
            
        # 4l  
        if "hzz4l" in self.channels:               
            self.dcnames.append( "comb_%s.txt"                   % ("hzz4l") );
                                                            
        # hzz2l2q
        if "hzz2l2q" in self.channels:               
            if self.mass >= 230:
                self.dcnames.append( "%s_VBF_8TeV.txt"               % ("hzz2l2q") );            
                if self.mass >= 400: self.dcnames.append( "%s_llallbMerged_8TeV.txt"      % ("hzz2l2q") );
                if self.mass <= 800: self.dcnames.append( "%s_llallb_8TeV.txt"            % ("hzz2l2q") );
                            
        # hwwlvqq
        if "hwwlvqq" in self.channels:               
            if self.mass >= 600: 
                self.dcnames.append( "%s_ggH%03i_el_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
                self.dcnames.append( "%s_ggH%03i_mu_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
                if not self.mass == 900: self.dcnames.append( "%s_ggH%03i_em_2jet_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
            if self.mass >= 170 and self.mass < 600:
                self.dcnames.append( "hwwlvjj_shape_8TeV_cpsq%02i_brnew%02i.txt" % (self.cpsq,self.brnew) );

#        if self.channel == "hwwlvqq_01j":
#            if self.mass >= 600: 
#                self.dcnames.append( "%s_ggH%03i_em_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
#
#        if self.channel == "hwwlvqq_01je":
#            if self.mass >= 600: 
#                self.dcnames.append( "%s_ggH%03i_el_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
#
#        if self.channel == "hwwlvqq_01jm":
#            if self.mass >= 600: 
#                self.dcnames.append( "%s_ggH%03i_mu_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
#
#        if self.channel == "hwwlvqq_2j":
#            if self.mass >= 600: 
#                self.dcnames.append( "%s_ggH%03i_em_2jet_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );

        # hww2l2v
        if "hww2l2v" in self.channels:               
            hwwpostfix = "EWKS";
            if self.mass <= 600:
                self.dcnames.append("hwwof_0j_shape_7TeV_"+hwwpostfix+".txt");
                self.dcnames.append("hwwof_1j_shape_7TeV_"+hwwpostfix+".txt");
                self.dcnames.append("hwwof_2j_shape_7TeV_"+hwwpostfix+".txt");
                self.dcnames.append("hwwsf_0j_cut_7TeV_"+hwwpostfix+".txt");
                self.dcnames.append("hwwsf_1j_cut_7TeV_"+hwwpostfix+".txt");
                self.dcnames.append("hwwsf_2j_cut_7TeV_"+hwwpostfix+".txt");
            #self.dcnames.append("hwwof_0j_shape_8TeV_"+hwwpostfix+".txt");
            self.dcnames.append("hwwof_1j_shape_8TeV_"+hwwpostfix+".txt");
            self.dcnames.append("hwwof_2j_shape_8TeV_"+hwwpostfix+".txt");
            self.dcnames.append("hwwsf_0j_cut_8TeV_"+hwwpostfix+".txt");
            self.dcnames.append("hwwsf_1j_cut_8TeV_"+hwwpostfix+".txt");
            self.dcnames.append("hwwsf_2j_cut_8TeV_"+hwwpostfix+".txt");

        # print self.dcnames;
        # check that the cards exist!!
        for i in range(len(self.dcnames)):
            if not os.path.isfile(self.curworkpath+"/"+self.dcnames[i]): 
                print "warning, Missing DC at "+self.curworkpath+"/"+self.dcnames[i]
                

    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
        
    def submitBatchJobMakeWS(self, command1, command2, workdir, wsName):
            
        currentDir = os.getcwd();
        print "Submitting batch job from: ", currentDir

        fnCore = os.path.splitext(os.path.basename(wsName))[0];
        fn = "condorScript_mkws_%s" % (fnCore);
        
        # create a dummy bash/csh
        outScript=open(fn+".sh","w");
        
        outScript.write('#!/bin/bash');
        outScript.write("\n"+'date');
        outScript.write("\n"+'source /uscmst1/prod/sw/cms/bashrc prod');
        outScript.write("\n"+'cd '+self.cwd);
        outScript.write("\n"+'eval `scram runtime -sh`');
        outScript.write("\n"+'cd -');
        outScript.write("\n"+'cp '+workdir+'/* .');
        outScript.write("\n"+'ls');    
        outScript.write("\n"+command1);
        outScript.write("\n"+command2);
        outScript.write("\n"+'cp ws_*.root '+workdir);
        outScript.close();
        
        # link a condor script to your shell script
        condorScript=open("subCondor_mkws_"+fn,"w");
        condorScript.write('universe = vanilla')
        condorScript.write("\n"+"Executable = "+fn+".sh")
        condorScript.write("\n"+'Requirements = Memory >= 199 &&OpSys == "LINUX"&& (Arch != "DUMMY" )&& Disk > 1000000')
        condorScript.write("\n"+'Should_Transfer_Files = YES')
        #condorScript.write("\n"+'Transfer_Input_Files = '+self.wsName)
        condorScript.write("\n"+'WhenToTransferOutput  = ON_EXIT_OR_EVICT')
        condorScript.write("\n"+'Output = out'+fnCore+'_$(Cluster).stdout')
        condorScript.write("\n"+'Error  = out'+fnCore+'_$(Cluster).stderr')
        condorScript.write("\n"+'Log    = out'+fnCore+'_$(Cluster).log')
        condorScript.write("\n"+'Notification    = Error')
        condorScript.write("\n"+'Queue 1')
        condorScript.close();
        
        # submit the condor job 
        
        os.system("condor_submit "+"subCondor_mkws_"+fn)                


    def hardFix1(self,dcname):
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/interf_ggH/#interf_ggH/ < new1.txt > new2.txt');
        os.system('mv new2.txt '+dcname);
        os.system('rm new1.txt');

