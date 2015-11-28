#include <iostream>
#include "TChain.h"
#include "TError.h"
#include "TRegexp.h"
#include <string>
#include <vector>

#include "baby_basic.hh"
#include "utilities.hh"

using namespace std;

namespace{
  const int NSYSTS = 18;
}

int main(int argc, char *argv[]){
  gErrorIgnoreLevel=6000; // Turns off ROOT errors due to missing branches                                                                    

  if(argc<1){
    cout<<"Format: ./run/change_weights.exe <infolder>=. <sample>=\"*.root\" <outfolder>=infolder"<<endl;
    return 1;
  }
  
  // Take command line arguments
  TString folder("."), sample("*.root"), outfolder(folder);
  if(argc>=2) folder=argv[1]; 
  if(argc>=3) sample=argv[2]; 
  if(argc>=4) outfolder=argv[3]; 
  if(!folder.EndsWith("/")) folder.Append("/");
  if(!outfolder.EndsWith("/")) outfolder.Append("/");

  //Setup chains
  baby_basic ch((folder+sample).Data());         
  ch.GetEntry(0); //Set branches to get size

  vector<TString> var_type, var; 
  vector<vector<TString> > var_val(NSYSTS);
  double nent_eff=0, sum_weff=0, sum_btag=0, sum_pu=0, sum_toppt=0;
  vector<double> sum_wpdf(ch.w_pdf().size(),0);
  vector<double> sum_bctag(ch.sys_bctag().size()), sum_udsgtag(ch.sys_udsgtag().size());
  vector<double> sum_fs_bctag(ch.sys_fs_bctag().size()), sum_fs_udsgtag(ch.sys_fs_udsgtag().size());
  vector<double> sum_isr(ch.sys_isr().size()), sum_spdf(ch.sys_pdf().size());
  vector<double> sum_mur(ch.sys_mur().size()), sum_muf(ch.sys_muf().size()), sum_murf(ch.sys_murf().size());
  double nent_zlep=0, sum_wlep=0, sum_fs_wlep=0;
  vector<double> sum_slep(ch.sys_lep().size()), sum_fs_slep(ch.sys_fs_lep().size());
  
  
  const int nentries = ch.GetEntries();
  //Loop over events and get sum of weights
  for(int ientry=0; ientry<nentries; ientry++){
    ch.GetEntry(ientry);

    //Progress meter
    if((ientry<100&&ientry%10==0) || (ientry<1000&&ientry%100==0) || (ientry<10000&&ientry%1000==0) || (ientry%10000==0)){
      if(isatty(1)){
        printf("\r[Change Weights] Calculating Weights: %i / %i (%i%%)",ientry,nentries,static_cast<int>((ientry*100./nentries)));
        fflush(stdout);
        if((ientry<100&&ientry+10>=nentries) || (ientry<1000&&ientry+100>=nentries) || (ientry<10000&&ientry+1000>=nentries) || (ientry>=10000&&ientry+10000>=nentries)) printf("\n");
      }
    }

    if(ch.weight()>0) nent_eff ++; else nent_eff--;
    sum_weff  +=  ch.weight()/(ch.eff_trig()*ch.w_lumi());
    sum_btag  +=  ch.w_btag();
    sum_pu    +=  ch.w_pu();
    sum_toppt +=  ch.w_toppt();
    for(unsigned int isys=0;isys<ch.w_pdf().size();isys++)            sum_wpdf[isys]        +=  ch.w_pdf().at(isys);
    for(unsigned int isys=0;isys<ch.sys_bctag().size();isys++)        sum_bctag[isys]       +=  ch.sys_bctag().at(isys);
    for(unsigned int isys=0;isys<ch.sys_udsgtag().size();isys++)      sum_udsgtag[isys]     +=  ch.sys_udsgtag().at(isys);
    for(unsigned int isys=0;isys<ch.sys_fs_bctag().size();isys++)     sum_fs_bctag[isys]    +=  ch.sys_fs_bctag().at(isys);
    for(unsigned int isys=0;isys<ch.sys_fs_udsgtag().size();isys++)   sum_fs_udsgtag[isys]  +=  ch.sys_fs_udsgtag().at(isys);
    for(unsigned int isys=0;isys<ch.sys_isr().size();isys++)          sum_isr[isys]         +=  ch.sys_isr().at(isys);
    for(unsigned int isys=0;isys<ch.sys_pdf().size();isys++)          sum_spdf[isys]        +=  ch.sys_pdf().at(isys);
    for(unsigned int isys=0;isys<ch.sys_mur().size();isys++)          sum_mur[isys]         +=  ch.sys_mur().at(isys);
    for(unsigned int isys=0;isys<ch.sys_muf().size();isys++)          sum_muf[isys]         +=  ch.sys_muf().at(isys);
    for(unsigned int isys=0;isys<ch.sys_murf().size();isys++)         sum_murf[isys]        +=  ch.sys_murf().at(isys);

    //Lepton weights
    if(ch.nleps()==0) nent_zlep++;
    else{
      sum_wlep     +=  ch.w_lep();
      sum_fs_wlep  +=  ch.w_fs_lep();
      for(unsigned int isys=0;isys<ch.sys_lep().size();isys++)        sum_slep[isys]        +=  ch.sys_lep().at(isys);
      for(unsigned int isys=0;isys<ch.sys_fs_lep().size();isys++)     sum_fs_slep[isys]     +=  ch.sys_fs_lep().at(isys);
    }
  }

  //Set type and var name
  var_type.push_back("float");      var.push_back("weight");
  var_type.push_back("float");      var.push_back("w_btag");            
  var_type.push_back("float");      var.push_back("w_pu");              
  var_type.push_back("float");      var.push_back("w_toppt");           
  var_type.push_back("vfloat");     var.push_back("w_pdf");             
  var_type.push_back("vfloat");     var.push_back("sys_bctag");         
  var_type.push_back("vfloat");     var.push_back("sys_udsgtag");       
  var_type.push_back("vfloat");     var.push_back("sys_fs_bctag");      
  var_type.push_back("vfloat");     var.push_back("sys_fs_udsgtag");    
  var_type.push_back("vfloat");     var.push_back("sys_isr");
  var_type.push_back("vfloat");     var.push_back("sys_pdf");
  var_type.push_back("vfloat");     var.push_back("sys_mur");
  var_type.push_back("vfloat");     var.push_back("sys_muf");
  var_type.push_back("vfloat");     var.push_back("sys_murf");
  var_type.push_back("float");      var.push_back("w_lep");
  var_type.push_back("float");      var.push_back("w_fs_lep");
  var_type.push_back("vfloat");     var.push_back("sys_lep");
  var_type.push_back("vfloat");     var.push_back("sys_fs_lep");

  //Calculate weights
  var_val[0].push_back("*"+to_string(nent_eff/sum_weff));
  var_val[1].push_back("*"+to_string(nent_eff/sum_btag));
  var_val[2].push_back("*"+to_string(nent_eff/sum_pu));
  var_val[3].push_back("*"+to_string(nent_eff/sum_toppt));
  for(unsigned int idx=0;idx<sum_wpdf.size();idx++)         var_val[4].push_back("*"+to_string(nent_eff/sum_wpdf[idx]));
  for(unsigned int idx=0;idx<sum_bctag.size();idx++)        var_val[5].push_back("*"+to_string(nent_eff/sum_bctag[idx]));
  for(unsigned int idx=0;idx<sum_udsgtag.size();idx++)      var_val[6].push_back("*"+to_string(nent_eff/sum_udsgtag[idx]));
  for(unsigned int idx=0;idx<sum_fs_bctag.size();idx++)     var_val[7].push_back("*"+to_string(nent_eff/sum_fs_bctag[idx]));
  for(unsigned int idx=0;idx<sum_fs_udsgtag.size();idx++)   var_val[8].push_back("*"+to_string(nent_eff/sum_fs_udsgtag[idx]));
  for(unsigned int idx=0;idx<sum_isr.size();idx++)          var_val[9].push_back("*"+to_string(nent_eff/sum_isr[idx]));
  for(unsigned int idx=0;idx<sum_spdf.size();idx++)         var_val[10].push_back("*"+to_string(nent_eff/sum_spdf[idx]));
  for(unsigned int idx=0;idx<sum_mur.size();idx++)          var_val[11].push_back("*"+to_string(nent_eff/sum_mur[idx]));
  for(unsigned int idx=0;idx<sum_muf.size();idx++)          var_val[12].push_back("*"+to_string(nent_eff/sum_muf[idx]));
  for(unsigned int idx=0;idx<sum_murf.size();idx++)         var_val[13].push_back("*"+to_string(nent_eff/sum_murf[idx]));
  //Calculate lepton weights
  var_val[14].push_back("*"+to_string((nent_eff-sum_wlep)/nent_zlep));
  var_val[15].push_back("*"+to_string((nent_eff-sum_fs_wlep)/nent_zlep));
  for(unsigned int idx=0;idx<sum_slep.size();idx++)         var_val[16].push_back("*"+to_string((nent_eff-sum_slep[idx])/nent_zlep));
  for(unsigned int idx=0;idx<sum_fs_slep.size();idx++)      var_val[17].push_back("*"+to_string((nent_eff-sum_fs_slep[idx])/nent_zlep));


  vector<TString> files = dirlist(folder,".root");
  TRegexp regex(sample,true);
  
  for(unsigned int i=0; i<files.size(); i++){
    if(files[i].Contains(regex)){
      cout<<"[Change Weights] File #"<<i+1<<endl;
      change_branch_one(folder, files[i], outfolder, var_type, var, var_val);
    }
  }
}