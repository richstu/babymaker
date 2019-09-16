// skim_scan_bymass.cxx: Separate signal scan by mass point
//  Takes mass points as arguments, outputs babies for each mass point
#include "utilities.hh"

#include <fstream>
#include <iostream>
#include <cmath>
#include <string>
#include <sstream>
#include <vector>
#include <stdlib.h>     /* atoi */
#include "TH2.h"
#include "TChain.h"
#include "TFile.h"
#include "TString.h"
#include "TMath.h"
#include "TSystem.h"
#include "TDirectory.h"
#include <ctime>

using namespace std;

int main(int argc, char *argv[]){
  time_t startTime;
  time(&startTime);

  TString outpath = "";
  TString infiles;
	string mgluino("1");
  vector<string> mlsps;
  int c(0), index(0);
	string next;
  while((c=getopt(argc, argv, "i:o:g:l:"))!=-1){
    switch(c){
		case 'i':
			infiles=optarg;
			break;
		case 'o':
			outpath=optarg;
			break;
    case 'g':
      mgluino=optarg;
      break;
    case 'l':
			index = optind - 1;
			while(index < argc) {
				next = argv[index];
				index++;
				if(next[0] == '-') break;
				else mlsps.push_back(next);
			}
			optind = index -1; 
      break;
    default:
      break;
    }
  }
  TChain tree("tree");
	int nfiles(0);
  nfiles = tree.Add(infiles+"/*.root");
  TChain treeglobal("treeglobal");
  treeglobal.Add(infiles+"/*.root");  
  //long nentries(tree.GetEntries());

  TString outfolder = outpath;
  outfolder.Remove(outfolder.Last('/')+1, outfolder.Length());
  if(outfolder!="") gSystem->mkdir(outfolder, kTRUE);

  time_t curTime;
  time(&curTime);
  // char time_c[100];
  //struct tm * timeinfo = localtime(&curTime);
  //strftime(time_c,100,"%Y-%m-%d %H:%M:%S",timeinfo);
 
  // Finding outfile names
  for(size_t i = 0; i<mlsps.size(); i++){
    time_t startloop;
    time(&startloop);
    TString outfile = "";
		TString mtag = "mGluino-"+mgluino+"_mLSP-"+mlsps.at(i);
    if (outpath==""){
      outfile=infiles;
      //outfile.Remove(0, outfile.Last('/')); outfile.ReplaceAll("*","");
      if(outfile.Contains(".root")) outfile.ReplaceAll(".root","_"+mtag+".root");
      else outfile += ("_"+mtag+".root");
      outfile.ReplaceAll(">=","ge"); outfile.ReplaceAll("<=","se"); outfile.ReplaceAll("&&","_");
      outfile.ReplaceAll(">","g"); outfile.ReplaceAll("<","s"); outfile.ReplaceAll("=","");
      outfile.ReplaceAll("(",""); outfile.ReplaceAll(")",""); outfile.ReplaceAll("+","");
      outfile.ReplaceAll("[",""); outfile.ReplaceAll("]",""); outfile.ReplaceAll("|","_");
      outfile.ReplaceAll("/","");
      //outfile = outfolder+outfile;
    } else {
      outfile = outpath;
      outfile.ReplaceAll("MASS_TAG",mtag);
    }
      
    TFile out_rootfile(outfile.Data(), "RECREATE");
    if(out_rootfile.IsZombie() || !out_rootfile.IsOpen()) return 1;
    out_rootfile.cd();

    //cout<<"Skimming the "<<nfiles<<" files in "<<infiles<<endl;
		TString cut("mgluino=="+mgluino+"&&mlsp=="+mlsps.at(i));
    TTree * ctree = tree.CopyTree(cut);
    TTree * ctreeglobal = treeglobal.CopyTree("1");
    if(ctree) ctree->Write();
    else cout<<"Could not find tree in "<<infiles<<endl;
    if(ctreeglobal)  ctreeglobal->Write();
    else cout<<"Could not find treeglobal in "<<infiles<<endl;
    
    time_t endloop;
    time(&endloop);
    int secs(floor(difftime(endloop,startloop)+0.5));
    cout<<"Written "<<outfile<<" with "<<ctree->GetEntries()<<" entries in "<<secs<<" seconds"<<endl;
    out_rootfile.Close();
  }
  time(&curTime);
  cout<<"Took "<< difftime(curTime,startTime)<<" seconds to skim "<< nfiles <<" files."<<endl;
}

