import os
import glob
import math
import array
import sys
import time
import ROOT


class singleWorkingPoint:

    def __init__(self, label, workpath, outpath, channels, mass, cpsq, brnew, productionMode=0):

    	self.label    = label;
        self.workpath = workpath;
        self.outpath  = outpath;
        self.cwd      = os.getcwd();

        self.channels = channels;
        self.mass     = mass;
        self.cpsq     = cpsq;
        self.brnew    = brnew;

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
            name1 = "%s_ggH%03i_el_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew);
            name2 = "%s_ggH%03i_mu_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew);                
            name3 = "%s_ggH%03i_em_2jet_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew);   
            if self.dcnames[i] == name1 or self.dcnames[i] == name2 or self.dcnames[i] == name3:
                print "hard fix 3 applied: ", self.dcnames[i]
                self.hardFix3(self.dcnames[i]);
            if "hwwof_" in self.dcnames[i] or "hwwsf_" in self.dcnames[i]:
                print "hard fix 1 applied: ", self.dcnames[i]                
                self.hardFix1(self.dcnames[i]);
                
            combineCmmd += " %s" % self.dcnames[i];

        combineCmmd += " > %s " % ccName;
                        
        # check if workspace exists
        if os.path.isfile(self.wsName) and not overwriteFile:
            print self.wsName, "already exists!"
            return;

        # make combined card
        time.sleep(0.5);
        os.system(combineCmmd);

        # turn into a workspace
        t2wOption = '';
        if self.prodMode > 0:
            # grab all the signal processes
            signalnames = self.getSignalProcesses(ccName);
            rnames = ['r_ggf','r_vbf','r_oth'];
            rvalue = [1,0,0];
            if self.prodMode == 2: rvalue = [0,1,0];            
            t2wOption += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose ";
            for i in range(len(signalnames)):
                if len(signalnames[i]) > 0: 
                    t2wOption += ' --PO \'map=';
                    for j in range(len(signalnames[i])):
                        if j == 0: t2wOption += signalnames[i][j]
                        else: t2wOption += ","+signalnames[i][j]
                    t2wOption += ':'+rnames[i]+'['+str(rvalue[i])+']\'';

        cmmd = "text2workspace.py %s -o %s %s" % (ccName,self.wsName,t2wOption);        

        if isBatch:
            time.sleep(1.);
            self.submitBatchJobMakeWS(cmmd,self.curworkpath,self.wsName);

        else:
            time.sleep(1.);
            os.system(cmmd);
        
        # come back
        os.chdir(self.cwd);

    ##########################################################################################################

    def runAsymLimit(self, isBatch):
        
        os.chdir( self.curworkpath );
        #os.chdir( self.outpath + "/outputs" );

        # combine options
        meth = '';
        if self.prodMode == 0:
            meth = "-M Asymptotic"        
            combineOptions = "--run expected";
            #if channel == "ALL": continue; 
            if "hzz4l" in self.channels or "hzzllll" in self.channels: 
                combineOptions += " --minosAlgo=stepping --X-rtd TMCSO_AdaptivePseudoAsimov --minimizerStrategy=0 --minimizerTolerance=0.0001 --cminFallback Minuit2:0.01 --cminFallback Minuit:0.001";
            #else: continue;

        if self.prodMode == 1 or self.prodMode == 2:
            meth = "-M MultiDimFit"        
            # grab all the signal processes
            ccName = "%s/workspaces/combine_%s_%03i_%02i_%02i.txt" % (self.outpath,self.label,self.mass,self.cpsq,self.brnew);
            signalnames = self.getSignalProcesses(ccName);
            rnames = ['r_ggf','r_vbf','r_oth'];
            poi = '';
            if self.prodMode == 1: poi = 'r_ggf'
            if self.prodMode == 2: poi = 'r_vbf'
            otherpois = [];
            for i in range(len(signalnames)):
                if len(signalnames[i]) > 0 and not rnames[i] == poi: otherpois.append(rnames[i]);

            combineOptions = "-t -1 --expectSignal=1";

            combineOptions += " -P %s --floatOtherPOIs=0 --algo=grid --points=100 --setPhysicsModelParameterRange %s=%02i,%02i" % (poi,poi,0,15);
            combineOptions += " --setPhysicsModelParameters "
            for i in range(len(otherpois)):
                if i == 0: combineOptions += "%s=0" % (otherpois[i]);
                else: combineOptions += ",%s=0" % (otherpois[i]);
        
        cmmd = "combine %s %s -n %s -m %03i %s" % (self.wsName,meth,self.biglabel,self.mass,combineOptions);
        print cmmd
        
        if not os.path.isfile(self.wsName):
            print "[runAsymLimit], ", self.wsName, "does not exist!"
        if os.path.isfile(self.oName):
            print "[runAsymLimit], ", self.oName, "already exists!"
            return;

        else:
            if isBatch: 
                time.sleep(1.);            
                self.submitBatchJobCombine(cmmd);
            else: 
                os.system(cmmd);
                time.sleep(1.);                            
                mvcmmd = "mv higgsCombine%s.Asymptotic.mH%03i.root %s/outputs/." % (self.biglabel,self.mass,self.outpath);
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
        outScript.write("\n"+'cp higgsCombine*'+self.label+'*.root '+self.outpath+'/outputs');
        outScript.close();
        
        # link a condor script to your shell script
        condorScript=open("subCondor_"+fn,"w");
        condorScript.write('universe = vanilla')
        condorScript.write("\n"+"Executable = "+fn+".sh")
        condorScript.write("\n"+'Requirements = Memory >= 199 &&OpSys == "LINUX"&& (Arch != "DUMMY" )&& Disk > 1000000')
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
            if self.mass >= 200:         
                #self.dcnames.append( "DataCard_2l2tau_PFIso_7TeV_LegacyPaper.txt" );
                #self.dcnames.append( "DataCard_2l2tau_PFIso_8TeV_LegacyPaper.txt" );
                #self.dcnames.append( "DataCard_H%03i_2l2tau_PFIso_7TeV_8TeV_LegacyPaper.txt"    % (self.mass) );
                if not self.mass == 3000: self.dcnames.append( "DataCard_2l2tau_7TeV.txt" );
                if not self.mass == 3000: self.dcnames.append( "DataCard_2l2tau_8TeV.txt" );                
            
        # 4l  
        if "hzz4l" in self.channels or "hzzllll" in self.channels:               
            self.dcnames.append( "comb_%s.txt"                   % ("hzz4l") );
                                                            
        # hzz2l2q
        if "hzz2l2q" in self.channels:               
            # if self.mass >= 230:
            #     self.dcnames.append( "%s_VBF_8TeV.txt"               % ("hzz2l2q") );            
            #     if self.mass >= 400: self.dcnames.append( "%s_llallbMerged_8TeV.txt"      % ("hzz2l2q") );
            #     if self.mass <= 800: self.dcnames.append( "%s_llallb_8TeV.txt"            % ("hzz2l2q") );
            if self.mass >= 230:
                self.dcnames.append( "hzz2l2q_Combined_8TeV.txt" );
                            
        # hwwlvqq
        if "hwwlvqq" in self.channels:               
            if self.mass >= 600: 
                self.dcnames.append( "%s_ggH%03i_el_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
                self.dcnames.append( "%s_ggH%03i_mu_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );
                self.dcnames.append( "%s_ggH%03i_em_2jet_%02i_%02i_unbin.txt" % ("hwwlvj",self.mass,self.cpsq,self.brnew) );     

            if self.mass >= 170 and self.mass < 600:
                self.dcnames.append( "hwwlvjj_shape_8TeV_cpsq%02i_brnew%02i.txt" % (self.cpsq,self.brnew) );

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
        #c1 = 'sed s/"kmax .."/"kmax \* "/ < '+dcname+' > new1.txt'
        #os.system(c1);
        os.system('sed s/interf_ggH/#interf_ww_ggH/ < '+dcname+' > new2.txt');
        os.system('mv new2.txt '+dcname);
        #os.system('rm new1.txt');

    def hardFix2(self,dcname):
        c1 = 'sed s/"CMS_hzz2l2tau_ZjetBkgMMEM"/"#CMS_hzz2l2tau_ZjetBkgMMEM"/ < '+dcname+' > new1.txt'
        os.system(c1);
        #os.system('sed s/interf_ggH/#interf_ggH/ < new1.txt > new2.txt');
        os.system('mv new1.txt '+dcname);
        os.system('rm new1.txt');        
    
    def hardFix3(self,dcname):
        c1 = 'sed s/CMS_scale_j/#CMS_scale_ww_j/ < '+dcname+' > new1.txt'
        os.system(c1);
        os.system('sed s/CMS_res_j/#CMS_res_ww_j/ < new1.txt > new2.txt');
        os.system('mv new2.txt '+dcname);
        os.system('rm new1.txt');   

