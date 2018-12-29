#!/bin/bash

#### Script to quickly run babymaker interactively. Format is:
####  ./scripts/cmsRun.sh <inFile> <nEvents=1000> <outName>"

## Storage location of files at UCSD:
inFile=/nfs-7/userdata/adorsett/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2_MINIAODSIM.root
outName=fullbaby_TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2_MINIAODSIM.root

inFile=/nfs-7/userdata/ana/Run2018C_EGamma_17Sep2018-v1.root
outName=fullbaby_Run2018C_EGamma_17Sep2018-v1.root

inFile=/nfs-7/userdata/ana/TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16MiniAODv3_PUMoriond17_94X_mcRun2_asymptotic_v3-v2.root
outName=fullbaby_TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16MiniAODv3_PUMoriond17_94X_mcRun2_asymptotic_v3-v2.root

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

