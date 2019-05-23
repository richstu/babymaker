// WEIGHT_TOOLS: Functions that deal with systematic weights

#ifndef H_WEIGHT_TOOLS
#define H_WEIGHT_TOOLS

#include "SimDataFormats/GeneratorProducts/interface/LHERunInfoProduct.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

class weight_tools{

private:
  std::vector<double> theoryWeights;
  std::vector<double> w_pu_up;
  std::vector<double> w_pu_nom;
  std::vector<double> w_pu_down;
  std::vector<TString> bad_pu17_datasets;
  bool bad_pu17;

public:
  // the enum index corresponds to the index of the variation
  enum variationType {
    nominal=1,
    muFup=2,
    muFdown=3,
    muRup=4,
    muRup_muFup=5,
    muRup_muFdown=6,
    muRdown=7,
    muRdown_muFup=8,
    muRdown_muFdown=9
  };

  float theoryWeight(variationType variation);
  void getTheoryWeights(edm::Handle<GenEventInfoProduct> gen_event_info);
  float pileupWeight(unsigned int ntrupv_mean, int type);
  float triggerEfficiency(int &nmus, int &nels, float &met, std::vector<float> &sys_trig);
  float topPtWeight(float top_pt1,float top_pt2);
  float isrWeight(float isrpt);
  void getPDFWeights(std::vector<float> &sys_pdf, std::vector<float> &w_pdf);
  weight_tools(TString outname);
  ~weight_tools();
};

#endif
