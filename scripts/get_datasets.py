#!/usr/bin/env python

# -------- Instructions for running on your laptop -----------
# one time pre-requisites: 
#    - intall go compiler https://golang.org/doc/install
#    - remember to set GOPATH (I just set it to the dasgoclient folder)
#    - then follow instructions at https://github.com/dmwm/dasgoclient
# every time:
#    - go to lxplus, generate proxy by running voms-proxy-init, it will be stored in some folder /tmp/x509..., remember the lxplus node
#    - copy the file x509... to the computer where you want to run the dasgoclient
#    - export X509_USER_PROXY=<wherever you put the file>
#    - test it, e.g.:
#         ./dasgoclient -query="parent dataset=/TTJets_SingleLeptFromTbar_genMET-150_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/MINIAODSIM"

import subprocess, sys, os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-y', '--year', type=int, default=2016)
parser.add_argument('--mc', action='store_true')
parser.add_argument('--data', action='store_true')
args = parser.parse_args()

if not args.mc and not args.data:
    sys.exit('Must specify at least one option of: --mc or --data.')

def print_dataset_line(datasets):
    nds = len(datasets)
    for i, ds in enumerate(datasets):
        if i==0:
            if nds==1: print '  datasets.append(["'+ds+'"])'
            else:      print '  datasets.append(["'+ds+'",'
        elif i==nds-1:
            print '                   "'+ds+'"])'
        else:
            print '                   "'+ds+'",'
    return 

names = [
    'TTJets_SingleLeptFromT_Tune', 'TTJets_SingleLeptFromT_genMET-150_Tune',
    'TTJets_SingleLeptFromTbar_Tune', 'TTJets_SingleLeptFromTbar_genMET-150_Tune',
    'TTJets_DiLept_Tune','TTJets_DiLept_genMET-150_Tune',
    'TTJets_HT-600to800_Tune','TTJets_HT-800to1200_Tune','TTJets_HT-1200to2500_Tune','TTJets_HT-2500toInf_Tune',
    'ST_s-channel_4f_leptonDecays','ST_t-channel_top_4f_inclusiveDecays_Tune','ST_t-channel_antitop_4f_inclusiveDecays_Tune',
    'ST_tW_top_5f_NoFullyHadronicDecays','ST_tW_antitop_5f_NoFullyHadronicDecays',
    'WJetsToLNu_Tune',
    'WJetsToLNu_HT-70To100_Tune','WJetsToLNu_HT-100To200_Tune','WJetsToLNu_HT-200To400_Tune','WJetsToLNu_HT-400To600_Tune',
    'WJetsToLNu_HT-600To800_Tune','WJetsToLNu_HT-800To1200_Tune','WJetsToLNu_HT-1200To2500_Tune','WJetsToLNu_HT-2500ToInf_Tune',
    'WJetsToQQ_HT-600ToInf_Tune',
    'DYJetsToLL_M-50_Tune',
    'DYJetsToLL_M-50_HT-70to100_Tune','DYJetsToLL_M-50_HT-100to200_Tune','DYJetsToLL_M-50_HT-200to400_Tune','DYJetsToLL_M-50_HT-400to600_Tune',
    'DYJetsToLL_M-50_HT-600to800_Tune','DYJetsToLL_M-50_HT-800to1200_Tune','DYJetsToLL_M-50_HT-1200to2500_Tune','DYJetsToLL_M-50_HT-2500toInf_Tune',
    'QCD_HT100to200_Tune', 'QCD_HT200to300_Tune', 'QCD_HT300to500_Tune','QCD_HT500to700_Tune',
    'QCD_HT700to1000_Tune','QCD_HT1000to1500_Tune','QCD_HT1500to2000_Tune','QCD_HT2000toInf_Tune',
    'ZJetsToNuNu_HT-100To200','ZJetsToNuNu_HT-200To400','ZJetsToNuNu_HT-400To600','ZJetsToNuNu_HT-600To800',
    'ZJetsToNuNu_HT-800To1200','ZJetsToNuNu_HT-1200To2500','ZJetsToNuNu_HT-2500ToInf',
    'ZJetsToQQ_HT600toInf',
    'TTGJets_Tune','TTZToQQ_Tune','TTZToLLNuNu_M-10_Tune','TTWJetsToQQ_Tune','TTWJetsToLNu_Tune',
    'TTTT_Tune','ttHTobb_M125',
    'WZTo1L1Nu2Q','WZTo1L3Nu','WZTo2L2Q','WZTo3LNu_Tune',
    'WWTo2L2Nu','WWToLNuQQ','ZZ_Tune',
    'WH_HToBB_WToLNu_M125','ZH_HToBB_ZToNuNu_M125',
    'SMS-T1tttt_mGluino-1200_mLSP-800','SMS-T1tttt_mGluino-1500_mLSP-100','SMS-T1tttt_mGluino-2000_mLSP-100'
]

tag = ''
if   args.year==2016: tag = 'RunIISummer16MiniAODv3'
elif args.year==2017: tag = 'RunIIFall17MiniAODv2'
elif args.year==2018: tag = 'RunIIAutumn18MiniAOD'

data_tier = 'MINIAODSIM'

# ------------- Monte Carlo samples ------------------
if args.mc:
    for name in names:
        output = subprocess.check_output(['./dasgoclient', '-query=dataset=/'+name+'*/'+tag+'*/'+data_tier,'status=*'])
        miniAODs = output.split()
        if args.year==2017:
            found = False
            datasets = []
            datasets_badpu = []
            for mini in miniAODs:
                if '_mtop1' in mini: continue
                elif 'PSweights' in mini: continue
                elif 'TuneCP5Down' in mini: continue
                elif 'TuneCP5Up' in mini: continue
                elif 'DoubleScattering' in mini: continue
                parent = subprocess.check_output('./dasgoclient -query="parent dataset='+mini+'"', shell=True)
                if 'PU2017' in parent:
                    found = True
                    datasets.append(mini)
                else:
                    datasets_badpu.append(mini)
            if not found: 
                if len(miniAODs)==0:
                    print '# missing dataset: ',name
                elif len(datasets_badpu)==1:
                    print '  datasets.append(["'+datasets_badpu[0]+'"]) # BAD PU!!! Alternative not available.'
                else:
                    print '**** Found multiple (bad) options:',[imini+'/n' for imini in miniAODs]
            else:
                print_dataset_line(datasets)
        else:
            datasets = []
            for mini in miniAODs:
                if '_mtop1' in mini: continue
                elif 'PSweights' in mini: continue
                elif 'TuneCP5Down' in mini: continue
                elif 'TuneCP5Up' in mini: continue
                elif 'DoubleScattering' in mini: continue
                elif 'FlatPU' in mini: continue
                datasets.append(mini)
            if len(datasets)==0:
                print '# missing dataset: ',name
            else:
                print_dataset_line(datasets)

# ----------------------- Data samples -------------------------
streams = ['MET', 'SingleElectron', 'SingleMuon', 'JetHT']
if args.year==2018: 
    streams = ['MET', 'EGamma', 'SingleMuon', 'JetHT']

tag = ''
runs = []
if   args.year==2016: 
    tag = '17Jul2018'
    runs = ['B','C','D','E','F','G','H']
elif args.year==2017: 
    tag = '31Mar2018'
    runs = ['B','C','D','E','F']
elif args.year==2018: 
    tag = '17Sep2018' # PromptReco for run D, hard-coded below
    runs = ['A','B','C','D']

data_tier = 'MINIAOD'

if args.data:
    for stream in streams:
        for run in runs:
            reco_tag = tag
            if args.year==2018 and run=='D': 
                reco_tag = 'PromptReco'

            output = subprocess.check_output(['./dasgoclient', '-query=dataset=/'+stream+'/Run'+str(args.year)+run+'*'+reco_tag+'*/'+data_tier])
            miniAODs = output.split()
            if len(miniAODs)==0:
                print '# missing dataset: /'+stream+'/Run'+str(args.year)+run+'*'+reco_tag+'*/'+data_tier
            for mini in miniAODs:
                print '  datasets.append(["'+mini+'"])'

print '\033[91m********************* CAUTION ****************************\033[0m'
print 'Before copying datasets to generate_crab_cfg.py, check for'
print 'undesired datasets that were accidentally selected or missing items!'
print 'e.g. MC: same dataset may be available in multiple generators'
print 'or with special generator options/phase spae, etc.'
print 'e.g. Data: same dataset may be available in multiple versions.'
print 'It seems for Re-reco those with different "ver" number are non-overlapping, while'
print 'those with different "-v" number are repeats. On the contrary, for PromptReco'
print 'different "-v" are non-overlapping. To be sure, please check'
print 'run list as follows:'
print './dasgoclient -query="run dataset=/MET/Run2016B-17Jul2018_ver1-v1/MINIAOD"'

