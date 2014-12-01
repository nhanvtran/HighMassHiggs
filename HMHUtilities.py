import os
import glob
import math
import array
import sys
import time
import ROOT


class singleWorkingPoint:

    def __init__(self, label, workpath, outpath, channels, mass, cpsq, brnew, productionMode=0, highmemory = False):

    	self.label    = label;
        self.workpath = workpath;
        self.outpath  = outpath;
        self.cwd      = os.getcwd();

        self.channels = channels;
        self.mass     = mass;
        self.cpsq     = cpsq;
        self.brnew    = brnew;

        self.highmemory = highmemory;

        # if production mode == 0, this is the default
        # if production mode == 1, this is ggH only
        # if production mode == 2, this is vbf only
        self.prodMode = productionMode;
        self.prodTag  = '';
        if self.prodMode == 1: self.prodTag = '_ggf';
        if self.prodMode == 2: self.prodTag = '_vbf';

        massdir = "%03i" % mass;
        bsmdir  = "cpsq%02i_brnew%02i" % (cpsq, brnew);
        self.curworkpath = self.workpath+"/work_"+massdir+"_"+bsmdir;1
        
        self.dcnames  = [];
        self.getDCNames();

        self.wsBaseName = "ws_%s_%03i_%02i_%02i%s.root" % (self.label,self.mass,self.cpsq,self.brnew,self.prodTag);
        self.wsName = "%s/workspaces/ws_%s_%03i_%02i_%02i%s.root" % (self.outpath,self.label,self.mass,self.cpsq,self.brnew,self.prodTag);
        self.wsExists = False;
        if os.path.isfile(self.wsName): self.wsExists = True;

        self.biglabel = "_%s_%03i_%02i_%02i%s" % (self.label,self.mass,self.cpsq,self.brnew,self.prodTag);
        self.oName = "%s/outputs/higgsCombine%s.Asymptotic.mH%03i.root" % (self.outpath,self.biglabel,self.mass);

	##########################################################################################################

    def createWorkspace(self, isBatch, overwriteFile=False):
        
        print "self.dcnames = ", self.dcnames
        if len(self.dcnames) == 0: return;
        
        # go to that dir
        os.chdir(self.curworkpath);

        # combine cards for a given channel
        ccName = "%s/workspaces/combine_%s_%03i_%02i_%02i.txt" % (self.outpath,self.label,self.mass,self.cpsq,self.brnew);
        combineCmmd = "combineCards.py ";
        for i in range(len(self.dcnames)): 
            #if 'interf_ggH' in open(self.dcnames[i]).read(): self.hardFix1(self.dcnames[i]);
            #if 'DataCard_2l2tau' in self.dcnames[i]: self.hardFix2(self.dcnames[i]);  
            # !!!hard fixes!!!
            # name1 = "%s_ggH%03i_el_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew);
            # name2 = "%s_ggH%03i_mu_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew);                
            # name3 = "%s_ggH%03i_em_2jet_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew);   
            # if self.dcnames[i] == name1 or self.dcnames[i] == name2 or self.dcnames[i] == name3:
            #     print "hard fix 3 applied: ", self.dcnames[i]
            
            ### remove all interf nusiances...
            #self.hardFix1D(self.dcnames[i]);
            # if "hwwof_" in self.dcnames[i] or "hwwsf_" in self.dcnames[i]:
            #     print "hard fix 1 applied: ", self.dcnames[i]                
            #     self.hardFix1(self.dcnames[i]);
            if "hwwlvjj" in self.dcnames[i]:
                print "hard fix 1 applied: ", self.dcnames[i]                
                self.hardFix1(self.dcnames[i]);
                
            combineCmmd += " %s" % self.dcnames[i];

        combineCmmd += " > %s " % ccName;
        print "combineCmmd = ",combineCmmd

        # check if workspace exists
        if os.path.isfile(self.wsName) and not overwriteFile:
            print self.wsName, "already exists!"
            return;

        # make combined card
        time.sleep(0.5);
        os.system(combineCmmd);

        ## hard fixes
        #self.hardFixE(ccName);
        #self.hardFixE1(ccName);
        #self.hardFixE2(ccName);
        #self.hardFixE1A(ccName,[1,3]);
        #self.hardFixE2A(ccName,[1,2,3,4,5,6,7,8,9]);
        # self.hardFix_paramRange(ccName);

        # turn into a workspace
        t2wOption = '';
        if self.prodMode > 0:

            ccNameAlt = "%s/workspaces/combine_%s_%03i_%02i_%02i%s.txt" % (self.outpath,self.label,self.mass,self.cpsq,self.brnew,self.prodTag);
            names = [];
            if self.prodMode == 2: names = ["ggH","GGH"];
            if self.prodMode == 1: names = ["qqH","VBF"];

            self.combineCardReparser(ccName,names,ccNameAlt);
            ccName = ccNameAlt
            # # grab all the signal processes
            # signalnames = self.getSignalProcesses(ccName);
            # rnames = ['r_ggf','r_vbf','r_oth'];
            # rvalue = [1,0,0];
            # if self.prodMode == 2: rvalue = [0,1,0];            
            # t2wOption += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose ";
            # for i in range(len(signalnames)):
            #     if len(signalnames[i]) > 0: 
            #         t2wOption += ' --PO \'map=';
            #         for j in range(len(signalnames[i])):
            #             if j == 0: t2wOption += signalnames[i][j]
            #             else: t2wOption += ","+signalnames[i][j]
            #         t2wOption += ':'+rnames[i]+'['+str(rvalue[i])+']\'';

        # if "hzz4l" in self.channels or "hzzllll" in self.channels: 
        #     cpsq_f = float(self.cpsq)/10.;
        #     brnew_f = float(self.brnew)/10.;
        #     newOption = "--setPhysicsModelParameters CMS_zz4l_csquared_BSM=%1.2f,CMS_zz4l_brnew_BSM=%1.2f --freezeNuisances CMS_zz4l_csquared_BSM,CMS_zz4l_brnew_BSM" % (cpsq_f,brnew_f);        
        #     t2wOption += newOption;

        cmmd = "text2workspace.py %s -o %s %s" % (ccName,self.wsName,t2wOption);        
        print "cmmd = ",cmmd;

        if isBatch:
            time.sleep(1.);
            self.submitBatchJobMakeWS(cmmd,self.curworkpath,self.wsName);

        else:
            time.sleep(1.);
            os.system(cmmd);
        
        # come back
        os.chdir(self.cwd);

    ##########################################################################################################

    def runAsymLimit(self, isBatch, method = "Asymptotic"):
        
        os.chdir( self.curworkpath );
        #os.chdir( self.outpath + "/outputs" );

        # combine options
        meth = '';
        if self.prodMode >= 0:
            ###meth = " -M Asymptotic"        
            meth = " -M "+method;
            #combineOptions = "--run blind";
            #combineOptions = "--run expected -v 99";
            combineOptions = "-t 0";
            #combineOptions = " -v 99 ";
            #if channel == "ALL": continue; 
            if "hzz4l" in self.channels or "hzzllll" in self.channels: 
                if method == "Asymptotic": combineOptions += " --minosAlgo=stepping --X-rtd TMCSO_AdaptivePseudoAsimov --minimizerStrategy=0 --minimizerTolerance=0.0001 --cminFallback Minuit2:0.01 --cminFallback Minuit:0.001";
                #if method == "Asymptotic": combineOptions += " --minosAlgo=stepping --minimizerStrategy=0 --minimizerTolerance=0.0001 --cminFallback Minuit2:0.01 --cminFallback Minuit:0.001";
                if method == "MaxLikelihoodFit": combineOptions += " --X-rtd TMCSO_AdaptivePseudoAsimov --minimizerStrategy=0 --minimizerTolerance=0.0001 --cminFallback Minuit2:0.01 --cminFallback Minuit:0.001";
                cpsq_f = float(self.cpsq)/10.;
                if self.cpsq == 00: cpsq_f = 0.01;
                if self.cpsq == 50: cpsq_f = 0.05;
                if self.cpsq == 30: cpsq_f = 0.03;
                brnew_f = float(self.brnew)/10.;
                combineOptions += " --setPhysicsModelParameters CMS_zz4l_csquared_BSM=%1.2f,CMS_zz4l_brnew_BSM=%1.2f " % (cpsq_f,brnew_f);        
                #combineOptions += "--freezeNuisances CMS_zz4l_csquared_BSM,CMS_zz4l_brnew_BSM"
                combineOptions += " --freezeNuisances CMS_zz4l_csquared_BSM,CMS_zz4l_brnew_BSM"

            #else: continue;

        # if self.prodMode == 1 or self.prodMode == 2:
        #     meth = "-M MultiDimFit"        
        #     # grab all the signal processes
        #     ccName = "%s/workspaces/combine_%s_%03i_%02i_%02i.txt" % (self.outpath,self.label,self.mass,self.cpsq,self.brnew);
        #     signalnames = self.getSignalProcesses(ccName);
        #     rnames = ['r_ggf','r_vbf','r_oth'];
        #     poi = '';
        #     if self.prodMode == 1: poi = 'r_ggf'
        #     if self.prodMode == 2: poi = 'r_vbf'
        #     otherpois = [];
        #     for i in range(len(signalnames)):
        #         if len(signalnames[i]) > 0 and not rnames[i] == poi: otherpois.append(rnames[i]);

        #     combineOptions = "-t -1 --expectSignal=1";

        #     combineOptions += " -P %s --floatOtherPOIs=0 --algo=grid --points=100 --setPhysicsModelParameterRange %s=%02i,%02i" % (poi,poi,0,15);
        #     combineOptions += " --setPhysicsModelParameters "
        #     for i in range(len(otherpois)):
        #         if i == 0: combineOptions += "%s=0" % (otherpois[i]);
        #         else: combineOptions += ",%s=0" % (otherpois[i]);
        
        #cmmd = "combine %s %s -n %s -m %03i %s -S 0" % (self.wsName,meth,self.biglabel,self.mass,combineOptions);
        if "blind" in combineOptions: self.biglabel = self.biglabel + "_blind"
        cmmd = "combine %s %s -n %s -m %03i %s" % (self.wsName,meth,self.biglabel,self.mass,combineOptions);
        print cmmd

        # redefine this...        
        self.oName = "%s/outputs/higgsCombine%s.Asymptotic.mH%03i.root" % (self.outpath,self.biglabel,self.mass);

        if not os.path.isfile(self.wsName):
            print "[runAsymLimit], ", self.wsName, "does not exist!"
            return;
        if os.path.isfile(self.oName):
            print "[runAsymLimit], ", self.oName, "already exists!"
            if method == "Asymptotic": return;

        # else:
        if isBatch: 
            time.sleep(1.);            
            self.submitBatchJobCombine(cmmd);
        else: 
            os.system(cmmd);
            time.sleep(1.);                            
            mvcmmd = "mv higgsCombine%s.*.mH%03i.root %s/outputs/." % (self.biglabel,self.mass,self.outpath);
            os.system(mvcmmd)
            mvcmmd = "mv mlfit*%s*.root %s/outputs/." % (self.biglabel,self.outpath);
            os.system(mvcmmd)

        os.chdir(self.cwd); 

    ##########################################################################################################

    def submitBatchJobMakeWS(self, command2, workdir, wsName):
            
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
        #outScript.write("\n"+command1);
        outScript.write("\n"+command2);
        outScript.write("\n"+'mv ws_*.root '+workdir);
        outScript.close();
        
        # link a condor script to your shell script
        condorScript=open("subCondor_mkws_"+fn,"w");
        condorScript.write('universe = vanilla')
        condorScript.write("\n"+"Executable = "+fn+".sh")

        if not self.highmemory: condorScript.write("\n"+'Requirements = Memory >= 199 &&OpSys == "LINUX"&& (Arch != "DUMMY" )&& Disk > 1000000')
        if self.highmemory:
            condorScript.write("\n"+"+BigMemoryJob = True")
            condorScript.write("\n"+'Requirements = Memory >= 199 &&OpSys == "LINUX"&& (Arch != "DUMMY" )&&Disk > 1000000')
            condorScript.write("\n"+'RequestMemory = 4000')

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

    ##########################################################################################################

    def submitBatchJobCombine(self, command):
            
        currentDir = os.getcwd();
        print "Submitting batch job from: ", currentDir

        fnCore = os.path.splitext(self.wsBaseName)[0];
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
        outScript.write("\n"+'mv higgsCombine*'+self.label+'*.root '+self.outpath+'/outputs');
        outScript.write("\n"+'mv mlfit*'+self.label+'*.root '+self.outpath+'/outputs');
        outScript.close();
        
        # link a condor script to your shell script
        condorScript=open("subCondor_"+fn,"w");
        condorScript.write('universe = vanilla')
        condorScript.write("\n"+"Executable = "+fn+".sh")
        
        if not self.highmemory: condorScript.write("\n"+'Requirements = Memory >= 199 &&OpSys == "LINUX"&& (Arch != "DUMMY" )&& Disk > 1000000')

        if self.highmemory:
            condorScript.write("\n"+"+BigMemoryJob = True")
            condorScript.write("\n"+'Requirements = Memory >= 199 &&OpSys == "LINUX"&& (Arch != "DUMMY" )&&Disk > 1000000')
            condorScript.write("\n"+'RequestMemory = 4000')
        
        condorScript.write("\n"+'Should_Transfer_Files = YES')
        #condorScript.write("\n"+'Transfer_Input_Files = '+self.wsBaseName)    
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

            # -rw-r--r-- 1 ntran us_cms 3627 May 13 00:16 hzz2l2v_500_8TeV_eegeq1jets.dat
            # -rw-r--r-- 1 ntran us_cms 3628 May 13 00:16 hzz2l2v_500_8TeV_mumueq0jets.dat
            # -rw-r--r-- 1 ntran us_cms 3503 May 13 00:16 hzz2l2v_500_8TeV_mumuvbf.dat
            # -rw-r--r-- 1 ntran us_cms 3624 May 13 00:16 hzz2l2v_500_8TeV_eeeq0jets.dat
            # -rw-r--r-- 1 ntran us_cms 3499 May 13 00:16 hzz2l2v_500_8TeV_eevbf.dat
            # -rw-r--r-- 1 ntran us_cms 3631 May 13 00:16 hzz2l2v_500_8TeV_mumugeq1jets.dat            
            if self.mass >= 200:         
                self.dcnames.append( "%s_%03i_8TeV_eeeq0jets.dat"    % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_eegeq1jets.dat"   % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_eevbf.dat"        % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_mumueq0jets.dat"  % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_mumugeq1jets.dat" % ("hzz2l2v",self.mass) );
                self.dcnames.append( "%s_%03i_8TeV_mumuvbf.dat"      % ("hzz2l2v",self.mass) );
            
        # hzz2l2t
        if "hzz2l2t" in self.channels:       
            if self.mass >= 200 and self.cpsq > 0 and self.cpsq < 20:         
                #self.dcnames.append( "DataCard_2l2tau_PFIso_7TeV_LegacyPaper.txt" );
                #self.dcnames.append( "DataCard_2l2tau_PFIso_8TeV_LegacyPaper.txt" );
                #self.dcnames.append( "DataCard_H%03i_2l2tau_PFIso_7TeV_8TeV_LegacyPaper.txt"    % (self.mass) );
                if not self.mass == 3000: self.dcnames.append( "DataCard_2l2tau_7TeV.txt" );
                if not self.mass == 3000: self.dcnames.append( "DataCard_2l2tau_8TeV.txt" );                

        # hzz2l2q
        if "hzz2l2q" in self.channels:               
            # if self.mass >= 230:
            #     self.dcnames.append( "%s_VBF_8TeV.txt"               % ("hzz2l2q") );            
            #     if self.mass >= 400: self.dcnames.append( "%s_llallbMerged_8TeV.txt"      % ("hzz2l2q") );
            #     if self.mass <= 800: self.dcnames.append( "%s_llallb_8TeV.txt"            % ("hzz2l2q") );
            if self.mass >= 230 and self.cpsq > 0 and self.cpsq < 20:
                self.dcnames.append( "hzz2l2q_Combined_8TeV.txt" );
                            
        # hwwlvqq
        if "hwwlvqq" in self.channels:               
            if self.mass >= 600 and self.cpsq > 0 and self.cpsq < 20: 
                self.dcnames.append( "%s_ggH%03i_mu_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
                self.dcnames.append( "%s_ggH%03i_em_2jet_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );     
                self.dcnames.append( "%s_ggH%03i_el_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
                #1 e,m,2j
                #2 2j,e,m
                #3 m,2j,e

            if self.mass >= 200 and self.mass < 600 and self.cpsq > 0 and self.cpsq < 20:
                self.dcnames.append( "hwwlvjj_shape_8TeV_cpsq%02i_brnew%02i.txt" % (self.cpsq,self.brnew) );

        # hww2l2v
        if "hww2l2v" in self.channels:               
            if self.cpsq > 0  and self.cpsq < 20:
                hwwpostfix = "EWKS";
                if self.cpsq == 10: hwwpostfix = "H125Bkg";
                # hwwpostfix = "EWKS";

                if (hwwpostfix == "EWKS" and self.mass >= 200) or (hwwpostfix == "H125Bkg"):
                    self.dcnames.append("hwwof_0j_shape_8TeV_"+hwwpostfix+".txt");
                    self.dcnames.append("hwwof_1j_shape_8TeV_"+hwwpostfix+".txt");
                    self.dcnames.append("hwwof_2j_shape_8TeV_"+hwwpostfix+".txt");            
                    self.dcnames.append("hwwsf_0j_cut_8TeV_"+hwwpostfix+".txt");
                    self.dcnames.append("hwwsf_1j_cut_8TeV_"+hwwpostfix+".txt");
                    self.dcnames.append("hwwsf_2j_cut_8TeV_"+hwwpostfix+".txt");
                    if self.mass <= 600:
                        self.dcnames.append("hwwof_0j_shape_7TeV_"+hwwpostfix+".txt");
                        self.dcnames.append("hwwof_1j_shape_7TeV_"+hwwpostfix+".txt");
                        self.dcnames.append("hwwof_2j_shape_7TeV_"+hwwpostfix+".txt");
                        self.dcnames.append("hwwsf_0j_cut_7TeV_"+hwwpostfix+".txt");
                        self.dcnames.append("hwwsf_1j_cut_7TeV_"+hwwpostfix+".txt");
                        self.dcnames.append("hwwsf_2j_cut_7TeV_"+hwwpostfix+".txt");
            
       # 4l  
        # if "hzz4l" in self.channels or "hzzllll" in self.channels:               
        #     # self.dcnames.append( "comb_%s.txt"                   % ("hzz4l") );
        #     # self.dcnames.append( 'hzz4l_2e2muS_7TeV_0.txt' );                
        #     # self.dcnames.append( 'hzz4l_2e2muS_7TeV_1.txt' );
        #     # self.dcnames.append( 'hzz4l_2e2muS_8TeV_0.txt' );            
        #     # self.dcnames.append( 'hzz4l_2e2muS_8TeV_1.txt' );            

        #     self.dcnames.append( 'hzz4l_4eS_8TeV_0.txt' );
        #     self.dcnames.append( 'hzz4l_4muS_8TeV_0.txt' );
        #     self.dcnames.append( 'hzz4l_2e2muS_8TeV_0.txt' );        
        #     self.dcnames.append( 'hzz4l_4eS_8TeV_1.txt' );
        #     self.dcnames.append( 'hzz4l_4muS_8TeV_1.txt' );
        #     self.dcnames.append( 'hzz4l_2e2muS_8TeV_1.txt' );
        #     self.dcnames.append( 'hzz4l_4eS_7TeV_0.txt' );
        #     self.dcnames.append( 'hzz4l_4muS_7TeV_0.txt' );
        #     self.dcnames.append( 'hzz4l_2e2muS_7TeV_0.txt' );
        #     self.dcnames.append( 'hzz4l_4eS_7TeV_1.txt' );
        #     self.dcnames.append( 'hzz4l_4muS_7TeV_1.txt' );
        #     self.dcnames.append( 'hzz4l_2e2muS_7TeV_1.txt' );
            
        #     # order 1 = 2e2mu, 4e, 4mu (70,71,80,81)
        #     # order 2 = 4e, 4mu, 2e2mu (70,71,80,81)
        #     # order 3 = 80, 81, 70, 71 (4e, 4mu, 2e2mu)      

        # 4l    
        if "hzz4l" in self.channels or "hzzllll" in self.channels:               
            # self.dcnames.append( "comb_%s.txt"                   % ("hzz4l") );
            # self.dcnames.append( 'hzz4l_2e2muS_7TeV_0.txt' );                
            # self.dcnames.append( 'hzz4l_2e2muS_7TeV_1.txt' );
            # self.dcnames.append( 'hzz4l_2e2muS_8TeV_0.txt' );            
            # self.dcnames.append( 'hzz4l_2e2muS_8TeV_1.txt' );            

            # self.dcnames.append( 'hzz4l_4eS_8TeV.txt' );
            # self.dcnames.append( 'hzz4l_4muS_8TeV.txt' );
            # self.dcnames.append( 'hzz4l_2e2muS_8TeV.txt' );
            # self.dcnames.append( 'hzz4l_4eS_7TeV.txt' );
            # self.dcnames.append( 'hzz4l_4muS_7TeV.txt' );
            # self.dcnames.append( 'hzz4l_2e2muS_7TeV.txt' );

            self.dcnames.append( 'hzz4l_2e2muS_8TeV_0.txt' );
            self.dcnames.append( 'hzz4l_4muS_8TeV_0.txt' );
            self.dcnames.append( 'hzz4l_4eS_8TeV_0.txt' );
            self.dcnames.append( 'hzz4l_4eS_8TeV_1.txt' );
            self.dcnames.append( 'hzz4l_4muS_8TeV_1.txt' );
            self.dcnames.append( 'hzz4l_2e2muS_8TeV_1.txt' );
            self.dcnames.append( 'hzz4l_4eS_7TeV_0.txt' );
            self.dcnames.append( 'hzz4l_4muS_7TeV_0.txt' );
            self.dcnames.append( 'hzz4l_2e2muS_7TeV_0.txt' );
            self.dcnames.append( 'hzz4l_4eS_7TeV_1.txt' );
            self.dcnames.append( 'hzz4l_4muS_7TeV_1.txt' );
            self.dcnames.append( 'hzz4l_2e2muS_7TeV_1.txt' );
            
            # order 1 = 2e2mu, 4e, 4mu (70,71,80,81)
            # order 2 = 4e, 4mu, 2e2mu (70,71,80,81)
            # order 3 = 80, 81, 70, 71 (4e, 4mu, 2e2mu)      


        # print self.dcnames;
        # check that the cards exist!!
        for i in range(len(self.dcnames)):
            if not os.path.isfile(self.curworkpath+"/"+self.dcnames[i]): 
                print "warning, Missing DC at "+self.curworkpath+"/"+self.dcnames[i]
                

    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    def getSignalProcesses(self,ccname):
        file = open(ccname,'r');
        # get all the signals
        #filelist = file.readlines();
        lists = [];
        signallist = [];
        for line in file:
            splitline = line.strip().split();
            lists.append( splitline );
            #print splitline
        for i in range(len(lists)-2):
            if lists[i][0] == "bin" and lists[i+1][0] == "process" and lists[i+2][0] == "process":
                #print len(lists[i]),len(lists[i+1]),len(lists[i+2])
                for j in range(1,len(lists[i+2])):
                    # do stuff
                    if int(lists[i+2][j]) <= 0: signallist.append(lists[i][j]+"/"+lists[i+1][j])
                break;
        del lists[:];
        #print signallist;
        # split up the signals
        ggfList = [];
        vbfList = [];
        othList = [];
        for i in range(len(signallist)):
            if "ggH" in signallist[i] or "GGH" in signallist[i]:   ggfList.append(signallist[i]);
            elif "qqH" in signallist[i] or "VBF" in signallist[i]: vbfList.append(signallist[i]);
            else: othList.append(signallist[i]);
        return [ggfList,vbfList,othList];


    def hardFix1(self,dcname):
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/int/#intfix/ < new1.txt > new2.txt');
        os.system('mv new2.txt '+dcname);
        #os.system('rm new1.txt');

    def hardFix1A(self,dcname):
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/int/#intfix/ < new1.txt > new2.txt');
        os.system('sed s/CMS_8TeV_hww_/#CMS_8TeV_hww_/ < new2.txt > new3.txt');
        os.system('sed s/CMS_hzz2l2q_/#CMS_hzz2l2q_/ < new3.txt > new4.txt');
        os.system('sed s/CMS_hzz2l2v_/#CMS_hzz2l2v_/ < new4.txt > new5.txt');        
        os.system('sed s/CMS_zz4l_/#CMS_zz4l_/ < new5.txt > new6.txt');        
        os.system('sed s/Deco_WJets0_/#Deco_WJets0_/ < new6.txt > new7.txt'); 
        os.system('sed s/CMS_hzz2l2tau_/#CMS_hzz2l2tau_/ < new7.txt > new8.txt'); 
        os.system('mv new8.txt '+dcname);
        os.system('rm new1.txt new2.txt new3.txt new4.txt new5.txt new6.txt new7.txt');        

    def hardFix1B(self,dcname):
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/int/#int/ < new1.txt > new2.txt');
        os.system('sed s/CMS/#CMS/ < new2.txt > new3.txt');
        os.system('sed s/Deco_WJets0_/#Deco_WJets0_/ < new3.txt > new4.txt');
        os.system('mv new4.txt '+dcname);
        os.system('rm new1.txt new2.txt new3.txt');

    def hardFix1C1(self,dcname):
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/int/#intfix/ < new1.txt > new2.txt');
        os.system('sed s/CMS_8TeV_hww_/#CMS_8TeV_hww_/ < new2.txt > new5.txt');
        os.system('sed s/CMS_zz4l_/#CMS_zz4l_/ < new5.txt > new6.txt');        
        os.system('sed s/Deco_WJets0_/#Deco_WJets0_/ < new6.txt > new7.txt'); 
        os.system('mv new7.txt '+dcname);
        os.system('rm new1.txt new2.txt new5.txt new6.txt');                      

    def hardFix1D(self,dcname):
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/int/#int/ < new1.txt > new2.txt');
        os.system('sed s/CMS_res/#CMS_res/ < new2.txt > new3.txt');
        os.system('sed s/CMS_scale/#CMS_scale/ < new3.txt > new4.txt');
        os.system('sed s/CMS_eff/#CMS_eff/ < new4.txt > new5.txt');        
        os.system('mv new5.txt '+dcname);
        os.system('rm new1.txt new2.txt new3.txt new4.txt');        

    def hardFix1D1(self,dcname):
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/int/#int/ < new1.txt > new2.txt');
        os.system('sed s/CMS_res/#CMS_res/ < new2.txt > new3.txt');
        os.system('sed s/CMS_scale/#CMS_scale/ < new3.txt > new4.txt');
        os.system('sed s/CMS_eff/#CMS_eff/ < new4.txt > new5.txt');        
        os.system('sed s/CMS_trigger/#CMS_trigger/ < new5.txt > new6.txt');        
        os.system('sed s/CMS_hzz/#CMS_hzz/ < new6.txt > new7.txt');                
        os.system('mv new7.txt '+dcname);
        os.system('rm new1.txt new2.txt new3.txt new4.txt new5.txt new6.txt');   

    def hardFix1D2(self,dcname):
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/int/#int/ < new1.txt > new2.txt');
        os.system('sed s/CMS_res/#CMS_res/ < new2.txt > new3.txt');
        os.system('sed s/CMS_scale/#CMS_scale/ < new3.txt > new4.txt');
        os.system('sed s/CMS_eff/#CMS_eff/ < new4.txt > new5.txt');        
        os.system('sed s/CMS_trigger/#CMS_trigger/ < new5.txt > new6.txt');        
        os.system('sed s/CMS_8TeV/#CMS_8TeV/ < new6.txt > new7.txt');                
        os.system('mv new7.txt '+dcname);
        os.system('rm new1.txt new2.txt new3.txt new4.txt new5.txt new6.txt');    

    def hardFix1D3(self,dcname):
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/int/#int/ < new1.txt > new2.txt');
        os.system('sed s/CMS_res/#CMS_res/ < new2.txt > new3.txt');
        os.system('sed s/CMS_scale/#CMS_scale/ < new3.txt > new4.txt');
        os.system('sed s/CMS_eff/#CMS_eff/ < new4.txt > new5.txt');        
        os.system('sed s/CMS_trigger/#CMS_trigger/ < new5.txt > new6.txt');        
        os.system('sed s/CMS_hwwlvj/#CMS_hwwlvj/ < new6.txt > new7.txt');                
        os.system('mv new7.txt '+dcname);
        os.system('rm new1.txt new2.txt new3.txt new4.txt new5.txt new6.txt');  

    def hardFixE(self,dcname):
        
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        f1 = open('new1.txt','r');

        fout = open("tmp.txt",'w');

        for line in f1:
            curline = line.strip();

            if ("lnN" in curline) or ("gmN" in curline) or ("shapeN" in curline) or ("lnU" in curline): curline = "#" + curline;
            fout.write( curline+'\n' );

        fout.close();
        os.system('mv tmp.txt '+dcname);      

    def hardFixE1(self,dcname):

        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        f1 = open('new1.txt','r');

        fout = open("tmp.txt",'w');

        for line in f1:
            curline = line.strip();

            if ("lnN" in curline) or ("gmN" in curline) or ("shapeN" in curline): 
                if not ("CMS" in curline): curline = "#" + curline;

            # if ("param" in curline) and ('-1,1' in curline): 
            #     updatedLine = curline.replace('[-1,1]','');
            #     curline = updatedLine;

            fout.write( curline+'\n' );

        fout.close();
        os.system('mv tmp.txt '+dcname); 

    def hardFixE2(self,dcname):

        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        f1 = open('new1.txt','r');

        fout = open("tmp.txt",'w');

        for line in f1:
            curline = line.strip();

            if ("lnN" in curline) or ("gmN" in curline) or ("shapeN" in curline): 
                if ("CMS" in curline): curline = "#" + curline;

            fout.write( curline+'\n' );

        fout.close();
        os.system('mv tmp.txt '+dcname);   


    def hardFixE1A(self,dcname,opt=[1]):

        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        f1 = open('new1.txt','r');

        fout = open("tmp.txt",'w');

        for line in f1:
            curline = line.strip();

            if ("lnN" in curline) or ("gmN" in curline) or ("shapeN" in curline): 
                if not ("CMS" in curline): 
                    if "QCDscale" in curline and (1 in opt): curline = "#" + curline;
                    if "int" in curline and      (2 in opt): curline = "#" + curline;
                    if "pdf" in curline and      (3 in opt): curline = "#" + curline;
                    if "Wjet" in curline and     (4 in opt): curline = "#" + curline;
                    if "Gen" in curline and      (5 in opt): curline = "#" + curline;
                    if "UEPS" in curline and     (6 in opt): curline = "#" + curline;
                    if "offshell" in curline and (7 in opt): curline = "#" + curline;
                    if "BRhiggs" in curline and  (8 in opt): curline = "#" + curline;
                    if "lumi_7" in curline and     (9 in opt): curline = "#" + curline;                
                    if "lumi_8" in curline and     (10 in opt): curline = "#" + curline;                

            fout.write( curline+'\n' );

        fout.close();
        os.system('mv tmp.txt '+dcname);          

    def hardFixE2A(self,dcname,opt=[1]):

        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        f1 = open('new1.txt','r');

        fout = open("tmp.txt",'w');

        for line in f1:
            curline = line.strip();

            if ("lnN" in curline) or ("gmN" in curline) or ("shapeN" in curline): 
                if not ("CMS" in curline): 
                    if "QCDscale" in curline and (1 in opt): curline = "#" + curline;
                    if "int" in curline and      (2 in opt): curline = "#" + curline;
                    if "pdf" in curline and      (3 in opt): curline = "#" + curline;
                    if "Wjet" in curline and     (4 in opt): curline = "#" + curline;
                    if "Gen" in curline and      (5 in opt): curline = "#" + curline;
                    if "UEPS" in curline and     (6 in opt): curline = "#" + curline;
                    if "offshell" in curline and (7 in opt): curline = "#" + curline;
                    if "BRhiggs" in curline and  (8 in opt): curline = "#" + curline;
                    if "lumi_7" in curline and     (9 in opt): curline = "#" + curline;                
                    if "lumi_8" in curline and     (10 in opt): curline = "#" + curline;                
                else: 
                    curline = "#" + curline;

            fout.write( curline+'\n' );

        fout.close();
        os.system('mv tmp.txt '+dcname);             

    def hardFixF1A(self,dcname,opt=1):

        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        f1 = open('new1.txt','r');

        fout = open("tmp.txt",'w');

        for line in f1:
            curline = line.strip();

            if ("lnN" in curline) or ("gmN" in curline) or ("shapeN" in curline) or ("param" in curline): 
                if not ("CMS" in curline): 
                    if "QCDscale" in curline and (1 in opt): curline = "#" + curline;
                    if "int" in curline and      (2 in opt): curline = "#" + curline;
                    if "pdf" in curline and      (3 in opt): curline = "#" + curline;
                    if "Wjet" in curline and     (4 in opt): curline = "#" + curline;
                    if "Gen" in curline and      (5 in opt): curline = "#" + curline;
                    if "UEPS" in curline and     (6 in opt): curline = "#" + curline;
                    if "offshell" in curline and (7 in opt): curline = "#" + curline;
                    if "BRhiggs" in curline and  (8 in opt): curline = "#" + curline;
                    if "lumi" in curline and     (9 in opt): curline = "#" + curline;

            fout.write( curline+'\n' );

        fout.close();
        os.system('mv tmp.txt '+dcname);                                      

    def hardFix_paramRange(self,dcname,opt=1):

        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        f1 = open('new1.txt','r');
        fout = open("tmp.txt",'w');

        for line in f1:
            curline = line.strip();
            if ("param" in curline) and ('-1,1' in curline): 
                updatedLine = curline.replace('[-1,1]','');
                curline = updatedLine;

            fout.write( curline+'\n' );

        fout.close();
        os.system('mv tmp.txt '+dcname);  

    def hardFix2(self,dcname):
        #c1 = 'sed s/"CMS_hzz2l2tau_ZjetBkgMMEM"/"#CMS_hzz2l2tau_ZjetBkgMMEM"/ < '+dcname+' > new1.txt'
        #os.system(c1);
        c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/interf_ggH/#interf_fix_ggH/ < new1.txt > new2.txt');
        os.system('mv new2.txt '+dcname);
        os.system('rm new1.txt');        
    
    def hardFix3(self,dcname):
        # c1 = 'sed s/"CMS_scale_j lnN"/"#CMS_scale_ww_j lnN"/ < '+dcname+' > new1.txt'
        # os.system(c1);
        # os.system('sed s/"CMS_res_j lnN"/"#CMS_res_j lnN"/ < new1.txt > new2.txt');
        # os.system('sed s/"intf_ggH            lnN"/"#intf_ggH lnN"/ < new2.txt > new3.txt');
        # os.system('mv new3.txt '+dcname);
        # os.system('rm new1.txt');   
        # os.system('rm new2.txt');   
        c1 = 'sed s/"CMS_scale_j"/"#CMS_scale_ww_j lnN"/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/"CMS_res_j lnN"/"#CMS_res_j lnN"/ < new1.txt > new2.txt');
        os.system('sed s/"intf_ggH            lnN"/"#intf_ggH lnN"/ < new2.txt > new3.txt');
        os.system('mv new3.txt '+dcname);
        os.system('rm new1.txt');   
        os.system('rm new2.txt');   

    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################

    def combineCardReparser(self, card, signals, ocard):
        print "card name = ",card
        file = open(card,'r');
        lists = [];
        listOfSignalsToRemove = [];

        sectionCtr = 1; 
        withinSectionCtr = 0;
        for line in file:
            splitline = line.strip()
            if "-----" in splitline: sectionCtr += 1;
            lists.append( splitline );
            if sectionCtr == 4:
                if withinSectionCtr > 0:
                    cursplitline  =  splitline.split();
                    if withinSectionCtr == 2: 
                        for j in range(len(cursplitline)):
                            #print cursplitline[j]
                            for k in range(len(signals)):
                                if signals[k] in cursplitline[j]: listOfSignalsToRemove.append(j);
                withinSectionCtr += 1;

        print "Number of signals to remove = ", len(listOfSignalsToRemove)

        sectionCtr = 1; 
        withinSectionCtr = 0;
        fout = open(ocard,'w');
        for i in range(len(lists)):
            splitline = lists[i]
            if "-----" in splitline: sectionCtr += 1;

            if sectionCtr >= 4 and not "-----" in splitline:
                newline = "";
                splitsplitline = splitline.split();
                #print len(splitsplitline);
                if sectionCtr == 4:
                    for j in range(len(splitsplitline)):
                        if not j in listOfSignalsToRemove: newline += splitsplitline[j] + " ";
                elif sectionCtr == 5 and ("lnN" in splitline or "lnU" in splitline or "shapeN2" in splitline):
                    for j in range(len(splitsplitline)):
                        if not (j-1) in listOfSignalsToRemove: newline += splitsplitline[j] + " ";                        
                elif sectionCtr == 5 and "gmN" in splitline:
                    for j in range(len(splitsplitline)):
                        if not (j-2) in listOfSignalsToRemove: newline += splitsplitline[j] + " ";                        
                elif sectionCtr == 5 and "gmN" in splitline:
                    for j in range(len(splitsplitline)):
                        if not (j-3) in listOfSignalsToRemove: newline += splitsplitline[j] + " ";                                                
                else: newline += splitline;
                newline += "\n";
                fout.write(newline);
            # elif "imax" in splitline:
            #     fout.write("imax * \n");
            elif "jmax" in splitline:
                fout.write("jmax * \n");
            elif "kmax" in splitline:
                fout.write("kmax * \n");
            else:
                fout.write(splitline + "\n");

        fout.close();
        #print "lists length = ", len(lists);
        # for i in range(len(filelist)):
        #     print filelist[i];



