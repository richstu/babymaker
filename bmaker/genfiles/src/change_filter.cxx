// change_filters: Reads in txt file and filters events accordingly

#include <ctime>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <set>
#include <getopt.h>
#include <sys/stat.h>

#include "TFile.h"
#include "TString.h"
#include "TTree.h"
#include "TSystem.h"
#include "TDirectory.h"

#include "utilities.hh"

using namespace std;

map<int, set<long> > getFilterList(string filter);
long change_filter_one(TString indir, TString name, TString outdir, 
  map<int, set<long> > filter_list);

int main(int argc, char *argv[]){
  time_t begtime, endtime;
  time(&begtime);

  TString filter("data/Run2017_MET.txt"), infolder("."), sample("*.root"), outfolder("out");
  int c(0);
  while((c=getopt(argc, argv, "f:i:s:o:"))!=-1){
    switch(c){
    case 'f':
      filter=optarg;
      break;
    case 'i':
      infolder=optarg;
      break;
    case 's':
      sample=optarg;
      break;
    case 'o':
      outfolder=optarg;
      break;
    default:
      break;
    }
  }

  if(filter==""){
    cout<<endl<<"Specify filter file and filter variable: "
        <<"./run/change_filter.exe -f <filter_file=csc2015_ee4sc_Jan13.txt> "
        <<"-i <infolder>=. -s <sample>=\"*.root\" -o <outfolder=out> "<<endl<<endl;
    return 1;
  }
    
  if(outfolder=="") outfolder=infolder;
  if(!infolder.EndsWith("/")) infolder.Append("/");
  if(!outfolder.EndsWith("/")) outfolder.Append("/");
  gSystem->mkdir(outfolder, kTRUE);

  map<int, set<long> > event_list = getFilterList(filter.Data());
  time(&endtime);
  int seconds = difftime(endtime, begtime);
  cout<<endl<<"Took "<<seconds<<" seconds to read filter event list"<<endl;

  long totentries(0);
  vector<TString> files = dirlist(infolder,sample);
  for(unsigned int i=0; i<files.size(); i++){
    cout<<"[Change filter] File "<<i+1<<"/"<<files.size()<<": "<<files[i]<<endl;
    totentries += change_filter_one(infolder, files[i], outfolder, event_list);
  }

  time(&endtime);
  seconds = difftime(endtime, begtime);
  float hertz = totentries; hertz /= seconds;
  cout<<endl<<"Took "<<seconds<<" seconds ("<<hoursMinSec(seconds)<<") for "<<totentries
      <<" events -> "<<roundNumber(hertz,1,1000)<<" kHz, "<<roundNumber(1000,2,hertz)
      <<" ms per event"<<endl<<endl;

}

map<int, set<long> > getFilterList(string filter){
  map<int, set<long> > event_list;

  ifstream infile(filter);
  string line;
  TString line_temp;

  while(getline(infile, line)){
    line_temp = line;
    line_temp.ReplaceAll(":"," ");
    istringstream iss(line_temp.Data());
    unsigned int irun, ils;
    long ievent;
    iss >> irun >> ils >> ievent;

    event_list[irun].insert(ievent);
  }
  infile.close();

  return event_list;
}


long change_filter_one(TString indir, TString name, TString outdir, 
                       map<int, set<long> > filter_list){

  //Set up old file/tree
  TFile *oldfile = new TFile(indir+name);
  TTree* oldtree = static_cast<TTree*>(oldfile->Get("tree"));

  int run = 0;
  Long64_t event = 0;
  bool pass(false);
  bool pass_goodv(false), pass_ecaldeadcell(false), pass_eebadsc(false), pass_cschalo_tight(false);
  bool pass_hbhe(false), pass_hbheiso(false), pass_badpfmu(false), pass_badchhad(false);
  bool pass_jets(false);
  bool pass_badcalib(false);

  //Set branch addresses
  oldtree->SetBranchAddress("run",&run);
  oldtree->SetBranchAddress("event",&event);
  oldtree->SetBranchAddress("pass",&pass);
  oldtree->SetBranchAddress("pass_goodv", &pass_goodv);
  oldtree->SetBranchAddress("pass_ecaldeadcell", &pass_ecaldeadcell);
  oldtree->SetBranchAddress("pass_eebadsc", &pass_eebadsc);
  oldtree->SetBranchAddress("pass_cschalo_tight", &pass_cschalo_tight);
  oldtree->SetBranchAddress("pass_hbhe", &pass_hbhe);
  oldtree->SetBranchAddress("pass_hbheiso", &pass_hbheiso);
  oldtree->SetBranchAddress("pass_badpfmu", &pass_badpfmu);
  oldtree->SetBranchAddress("pass_badchhad", &pass_badchhad);
  oldtree->SetBranchAddress("pass_jets", &pass_jets);
  oldtree->SetBranchAddress("pass_badcalib", &pass_badcalib);

  //Set up new tree
  name.ReplaceAll(".root","_refilter.root");
  TFile* newfile = new TFile(outdir+name,"recreate");
  TTree* newtree = oldtree->CloneTree(0);

  long nentries = oldtree->GetEntries();

  for(long i=0; i<nentries; i++){
    oldtree->GetEntry(i);

    map<int, set<long> >::iterator imap = filter_list.find(run);
    if(imap==filter_list.end()){ //If run not in filter list, events pass 
      pass_badcalib=true; 
      pass = pass_goodv && pass_ecaldeadcell && pass_eebadsc && pass_cschalo_tight && pass_hbhe &&
             pass_hbheiso && pass_badpfmu && pass_badchhad && pass_jets && pass_badcalib;
      newtree->Fill();
      continue;      
    }
    else if(imap->second.find(event)==imap->second.end()){ //If event not in filter list, event passes
      pass_badcalib=true; 
      pass = pass_goodv && pass_ecaldeadcell && pass_eebadsc && pass_cschalo_tight && pass_hbhe &&
             pass_hbheiso && pass_badpfmu && pass_badchhad && pass_jets && pass_badcalib;
      newtree->Fill();
      continue;  
    }
    else{ //If run and event are in filter list, event fails
      pass_badcalib=false;
      pass=false;
      newtree->Fill();
    }
  }
  newtree->AutoSave();
  delete oldfile;
  delete newfile;

  return nentries;
}
