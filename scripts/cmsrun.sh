#!/bin/bash

#### Script to quickly run babymaker interactively. Format is:
####  ./scripts/cmsRun.sh <inFile> <nEvents=1000> <outName>"

## Storage location of files at UCSD:
inFile=/nfs-7/userdata/adorsett/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2_MINIAODSIM.root
outName=fullbaby_TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2_MINIAODSIM.root

inFile=/nfs-7/userdata/ana/Run2018C_EGamma_17Sep2018-v1.root
outName=fullbaby_Run2018C_EGamma_17Sep2018-v1.root

inFile=/home/users/ana/Run2017F_MET_31Mar2018_v1.root
outName=fullbaby_Run2017F_MET_31Mar2018_v1.root

# inFile=/home/users/ana/TTJets_SingleLeptFromTbar_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2_PU2017_12Apr2018_94X_mc2017_realistic_v14-v1.root
# outName=fullbaby_TTJets_SingleLeptFromTbar_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2.root

inFile=/hadoop/cms/store/user/ana/test/SMS-T1tttt_TuneCP2_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2_PUFall17Fast_pilot_94X_mc2017_realistic_v15.root
outName=fullbaby_SMS-T1tttt_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2Fast.root

# inFile=/hadoop/cms/store/user/ana/test/SMS-T1tttt_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16MiniAODv3_PUSummer16v3Fast_94X_mcRun2_asymptotic_v3.root
# outName=fullbaby_SMS-T1tttt_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16MiniAODv3_PUSummer16v3Fast.root

inFile=/hadoop/cms/store/user/ana/test/SMS-T1tttt_TuneCP2_13TeV-madgraphMLM-pythia8_RunIIAutumn18MiniAOD_PUFall18Fast_102X_upgrade2018_realistic_v15.root
outName=fullbaby_SMS-T1tttt_TuneCP2_13TeV-madgraphMLM-pythia8_RunIIAutumn18MiniAOD_PUFall18Fast_102X.root

nEvents="1000"

json=do_not_want_json # If it can't find the file, it doesn't pre-apply the JSON
# json="babymaker/data/json/golden_Cert_271036-275125_13TeV_PromptReco_Collisions16.json"

if (( "$#" > 0 ))
then
    inFile=$1
fi
if (( "$#" > 1 ))
then
    nEvents=$2
fi
if (( "$#" > 2 ))
then
    outName="outputFile="$3
fi

if [[ ($outName != *"outputFile"*) ]]
then
    outName="outputFile="$outName
fi
   
cmsRun bmaker/python/bmaker_full_cfg.py inputFiles=file:$inFile nEvents=$nEvents json=$json $outName 2>&1 | tee logout.log

