#!/usr/bin/env python

###### Script that adds the era to data root files that have been split by run (and have the run number in the name)
import os, sys, subprocess
import pprint
import glob
import argparse

## Parsing input arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("-i", "--infolder", help="Folder to find root files in", 
                    default="/net/cms2/cms2r0/babymaker/babies/2018_12_17/data/unskimmed/")
parser.add_argument("-o", "--outfolder", help="Folder to write files to", 
                    default="/net/cms2/cms2r0/babymaker/babies/2018_12_17/data/unskimmed/")
parser.add_argument("-y", "--year", type=int, help="Year of the data.", 
                    default=2016)
parser.add_argument("-e", "--execute", help="Execute", action='store_true')
args = parser.parse_args()
args.outfolder = args.outfolder+"/"

eras = []
if args.year==2016:
  eras = [["B", [272007, 275376]], ["C", [275657, 276283]], ["D", [276315, 276811]], ["E", [276831, 277420]], 
          ["F", [277772, 278808]], ["G", [278820, 280385]], ["H", [280919, 284044]]] 
elif args.year==2017:
  eras = [["B", [297046, 299329]], ["C", [299368, 302029]], ["D", [302030, 303434]], ["E", [303824, 304797]], 
          ["F", [305040, 306462]]] 
elif args.year==2018:
  eras = [["A", [315252, 316995]], ["B", [317080, 319310]], ["C", [319337, 320065]], ["D", [320673, 325175]]] 

## Create output folder
if not os.path.exists(args.outfolder):
  print "\nCreating "+args.outfolder
  os.system("mkdir -p "+args.outfolder)

noera_runs = []
nfiles = 0
files = glob.glob(args.infolder+'/*.root')
for ifile,file in enumerate(files):
  outfile = file.replace(args.infolder, args.outfolder)

  ## Parsing run from file name
  run = file.split('runs')[-1]
  run = int(run.split('.root')[0])

  ## Finding era for run
  found_era = False
  for era in eras:
    if run >= era[1][0] and run <= era[1][1]: 
      outfile = outfile.replace("baby_", "baby_Run"+str(args.year)+era[0]+"_")
      found_era = True
      break
  if not found_era: 
    noera_runs.append(run)
  else:
    ## Moving file
    cmd = "mv -i "+file+" "+outfile
    if (ifile==0): 
      print cmd
    if (args.execute): 
      os.system(cmd)
    nfiles += 1

## Final printouts
if len(noera_runs)>0:
  print "\nNot found era for runs "
  print noera_runs
print "\nCopied and renamed "+str(nfiles)+" files into "+args.outfolder+"\n\n"

if not args.execute:
  print "If printed command looks ok, use -e to execute"
