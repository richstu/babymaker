from ROOT import TH2F, TChain, TFile, TString, TMath, TSystem
import os, sys, glob, argparse

def sendSplitScan(infile):
	tree = TChain('tree')
	tree.Add(infile+'/unsplit/*.root')
	
	sig = 'T1tttt_'
	outfile = glob.glob(infile+'/unsplit/*.root')[0].replace('unsplit','split').replace(sig,sig+'MASS_TAG_')
	if not os.path.exists(outfile.split('fullbaby')[0]):
		os.mkdir(outfile.split('fullbaby')[0])
	mass_plane = TH2F('mglu_vs_mlsp','mglu_vs_mlsp',3000,-0.5,2999.5,3000,-0.5,2999.5)
	tree.Project('mglu_vs_mlsp','mgluino:mlsp','','colz')

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
				if mgluino in mass_dict.keys():
					mass_dict[mgluino].append(mlsp)
				else:
					mass_dict.update({mgluino:[mlsp]})
	print 'Submitting jobs for %i mass points' % n
	n = 0
	for mp in mass_dict:
		os.system('JobSetup.csh')
		lsps = ''
		masses = 0
		for m in mass_dict[mp]:
			masses += 1
			lsps += '%i ' % m
			if masses == 5:
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
    parser = argparse.ArgumentParser(description="Submits jobs to separate signal MC by mass points",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i","--input_dir", default=None,
                        help="Directory with unsplit babies")
    args = parser.parse_args()

    sendSplitScan(args.input_dir)



