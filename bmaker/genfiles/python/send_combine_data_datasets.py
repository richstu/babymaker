#!/usr/bin/env python

###### Script to send jobs to merge ntuples
import os, sys, subprocess
import pprint
import glob
import json
import string
import time
import pprint

# Setting folders
year = 2017
datasets, infolder, outfolder, jsonfile = '', '', '', ''

if year==2016:
    datasets = 'txt/alldata_2016_2017.txt'
    infolder  = '/net/cms2/cms2r0/babymaker/babies/2019_01_05/data/unprocessed/'
    outfolder = '/net/cms2/cms2r0/babymaker/babies/2019_01_05/data/unskimmed/'
    jsonfile = '../../data/json/golden_Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16.json'
elif year==2017:
    datasets = 'txt/alldata_2016_2017.txt'
    infolder  = '/net/cms2/cms2r0/babymaker/babies/2018_12_17/data/unprocessed/'
    outfolder = '/net/cms2/cms2r0/babymaker/babies/2018_12_17/data/unskimmed/'
    jsonfile = '../../data/json/golden_Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17.json'
elif year==2018:
    datasets = 'txt/alldata_2018.txt'
    infolder  = '/net/cms2/cms2r0/babymaker/babies/2019_01_04/data/unprocessed/'
    outfolder = '/net/cms2/cms2r0/babymaker/babies/2019_01_04/data/unskimmed/'
    jsonfile = '../../data/json/golden_Cert_314472-325175_13TeV_PromptReco_Collisions18.json'

runs_file = 1 # Number of runs in each ntuple


runs=[]
with open(jsonfile) as jfile:
  for line in jfile:
    for word in line.split():
      if '"' in word: 
        word = word.split('"')[1]
        runs.append(word)

# Dividing runs into sets of "runs_file" elements
runs = [runs[i:i+runs_file] for i in xrange(0, len(runs), runs_file)]

# Sending jobs for each set of runs
os.system("JobSetup.csh")
for run in runs:
  cmd = "JobSubmit.csh ./run/wrapper.sh ./run/combine_datasets.exe -i "+infolder+" -o "+outfolder+" -n Run"+str(year)+" -f "+datasets+" -b "+run[0]+" -e "+run[-1]
  # print cmd
  os.system(cmd)

print 'Number of runs:', len(runs)

sys.exit(0)
