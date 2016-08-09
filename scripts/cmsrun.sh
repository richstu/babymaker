#!/bin/bash

#### Script to quickly run babymaker interactively. Format is:
####  ./scripts/cmsRun.sh <inFile> <nEvents=1000> <outName>"

## Storage location of files at UCSD/lxplus, two examples:
# inFile=/afs/cern.ch/user/m/manuelf/work/data/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring15MiniAODv2_74X_mcRun2_asymptotic_v2-v1_MINIAODSIM.root
# inFile=/nfs-7/userdata/ana/TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring16MiniAODv1_PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1.root

inFile=/net/cms2/cms2r0/babymaker/miniaod/RunIISpring16MiniAODv2__TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8__MINIAODSIM__PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1__00000__001AFDCE-C33B-E611-B032-0025905D1C54.root
outName="fullbaby_TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISpring16MiniAODv2_PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic.root"

# inFile=/net/cms2/cms2r0/babymaker/miniaod/TTJets_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring16MiniAODv2_PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1.root
# outName="fullbaby_TTJets_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring16MiniAODv2_PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1.root"

# inFile=/net/cms2/cms2r0/babymaker/miniaod/SMS-TChiWH_WToLNu_HToBB_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring16MiniAODv2_PUSpring16Fast_80X_mcRun2_asymptotic_2016_miniAODv2.root
# outName="fullbaby_SMS-TChiWH_WToLNu_HToBB_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring16MiniAODv2_PUSpring16Fast_80X_mcRun2_asymptotic_2016_miniAODv2.root"

nEvents="10000"

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
   
if [[ ($inFile == *"store"*) && ($inFile != *"hadoop"*) ]]
then
    cmsRun bmaker/python/bmaker_full_cfg.py inputFiles=$inFile nEvents=$nEvents json=$json $outName 2>&1 | tee logout.log
else 
    cmsRun bmaker/python/bmaker_full_cfg.py inputFiles=file:$inFile nEvents=$nEvents json=$json $outName 2>&1 | tee logout.log
fi

