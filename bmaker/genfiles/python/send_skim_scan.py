#! /usr/bin/env python

from ROOT import TH2F, TChain, TFile, TString, TMath, TSystem
import os, sys, glob, argparse

def sendSplitScan(infile, model):
	tree = TChain('tree')
	tree.Add(infile+'/*.root')
	
	if (model=='T5tttt'): 
		model = 'T5tttt_dM175'
	elif model!='T1tttt' and model!='T2tt':
		print "Unknown model"
		sys.exit(0)
	outfile = glob.glob(infile+'/*.root')[0].replace('unsplit','unprocessed').replace(model+'_',model+'_MASS_TAG_')
	if not os.path.exists(outfile.split('fullbaby')[0]):
		os.mkdir(outfile.split('fullbaby')[0])
	mass_plane = TH2F('mglu_vs_mlsp','mglu_vs_mlsp',3000,-0.5,2999.5,3000,-0.5,2999.5)
	tree.Project('mglu_vs_mlsp','mgluino:mlsp','mgluino<2601','colz')

	mass_dict = {}
	print 'Getting mass points...'
	n = 0
	for y in range(mass_plane.FindFirstBinAbove(0,2),mass_plane.FindLastBinAbove(0,2)+1):
		for x in range(mass_plane.FindFirstBinAbove(0,1),mass_plane.FindLastBinAbove(0,1)+1):
			if mass_plane.GetBinContent(x,y) > 0:
				mgluino = mass_plane.GetYaxis().GetBinCenter(y)	
				mlsp = mass_plane.GetYaxis().GetBinCenter(x)	
# 				print 'Found mass point: mgluino = %i, mlsp = %i' % (mgluino, mlsp)
				n += 1
				ioutfile = outfile.replace("MASS_TAG","mGluino-{:.0f}_mLSP-{:.0f}".format(mgluino, mlsp))
				if not os.path.exists(ioutfile):
					if mgluino in mass_dict.keys():
						mass_dict[mgluino].append(mlsp)
					else:
						mass_dict.update({mgluino:[mlsp]})
# 	print 'Submitting jobs for %i mass points' % n

	n = 0
	for mp in mass_dict:
		os.system('JobSetup.csh')
		lsps = ''
		masses = 0
		for m in mass_dict[mp]:
			masses += 1
			lsps += '%i ' % m
			if masses == 2:
				cmd = 'JobSubmit.csh ./run/wrapper.sh ./run/skim_scan_bymass.exe -i %s -o %s -g %i -l %s' % (infile, outfile, mp, lsps)
				print 'Submitting job for mgluino = %i, mlsp = %s' % (mp, lsps)
				os.system(cmd)
				n += 1
				masses = 0
				lsps = ''
		if masses > 0:
			cmd = 'JobSubmit.csh ./run/wrapper.sh ./run/skim_scan_bymass.exe -i %s -o %s -g %i -l %s' % (infile, outfile, mp, lsps)
			print 'Submitting job for mgluino = %i, mlsp = %s' % (mp, lsps)
			os.system(cmd)
			n += 1

	print 'Submitted %i jobs' % n


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Submits jobs to separate modelnal MC by mass points",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i","--input_dir", default=None,
                        help="Directory with unsplit babies")
    parser.add_argument("-m","--model", default=None,
                        help="Directory with unsplit babies")
    args = parser.parse_args()

    if 'unsplit' not in args.input_dir:
    	sys.exit("Unexpected input dir, expecting subdir \'unsplit\'")

    sendSplitScan(args.input_dir, args.model)



