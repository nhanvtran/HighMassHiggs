Setting up the high mass combination...

The main script is:
runHMHcombination.py

The helper classes are in:
HMHUtilities.py

The structure of the directories is the following (example):

    svnpath = "/uscms_data/d2/ntran/physics/HighMassHiggs/svn/cardlinks"    
    workdir = "/uscms_data/d2/ntran/physics/HighMassHiggs/combine_052314/CMSSW_6_1_1/src/HighMassHiggs/tmpwork_080614/tmpwork"
    outpath = "/eos/uscms/store/user/ntran/HighMassHiggsOutput/workingarea_080614"

svnpath is where the cards are located (copy of SVN)
workdir is a path where temporary working directories are created for each phase space point
outpath is where the final results go, it should have two directories inside "workspaces" and "outputs"

The combination works in two steps, the (1) "text2workspace" step which creates intermediate worskpaces and the (2) "combine" step which runs the full combination: 

Examples to run the code are:

(1)
python runHMHcombination.py -b --makeWorkingDirs --mkWkspace --brnew 00 --mass 700 --cpsq 10 --isBatch --highMemory

(2)
python runHMHcombination.py -b --runLimits --brnew 00 --mass 700 --cpsq 10 --isBatch --highMemory

The full set of options can be found in the script.  Just some explanation:

--makeWorkingDirs sets up the working directories for a given phase space point
--mkWkspace runs step (1)
--runLimits runs step (2)

--isBatch is a flag to submit to the condor batch system
--highMemory is a flag for when --isBatch is true, to submit to the high memory nodes

--brnew, --mass, --cpsq set the working point that you want to use, if you do not set them, the script will run over all the points specified in the file, example:
mass  = [200,250,300,350,400,500,600,700,800,900,1000];

