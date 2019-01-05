babymaker
==============

CMSSW code to generate babies (small flat ntuples) from MINIAOD

  * [Code setup](#code-setup)
  * [Adding new branches](#adding-new-branches)
  * [Getting an flist](#getting-an-flist)
  * [Conventions in babymaker](#conventions-in-babymaker)

#### Code setup for full Run II dataset: CMSSW 10_2_6

    export SCRAM_ARCH=slc6_amd64_gcc700
    cmsrel CMSSW_10_2_6
    cd CMSSW_10_2_6/src
    cmsenv
    git cms-init
    git cms-merge-topic lathomas:L1Prefiring_10_2_6                         # only if 2016 MC or 2017 MC
    git cms-addpkg RecoMET/METFilters                                       # only if 2017 data/MC or 2018 data/MC
    git cms-merge-topic cms-met:METFixEE2017_949_v2_backport_to_102X        # only if 2017 data/MC
    scram b
    git clone git@github.com:richstu/babymaker
    cd babymaker
    ./compile.sh

#### Adding new branches

To add new branches to the tree, you first create the new branch in
`babymaker/variables/full` where the type and name are specified.
The code in `babymaker/bmaker/genfiles/src/generate_baby.cxx` automatically generates
the files 

    babymaker/bmaker/interface/baby_base.hh
    babymaker/bmaker/interface/baby_full.hh
    babymaker/bmaker/src/baby_base.cc
    babymaker/bmaker/src/baby_full.cc

which have the c++ code that defines the class `baby_full` with the tree, all the branches,
automatic vector clearing in the `baby_full::Fill` method, and other useful functions.

The branches are filled in the `bmaker_full::analyze` method in 
`babymaker/bmaker/plugins/bmaker_full.cc`. Functions that define physics quantities,
like isolation or electron ID, are defined in `babymaker/bmaker/src/*_tools.cc`.

#### Post-processing of produced babies

See [bmaker/genfiles/README.md](bmaker/genfiles/README.md) for detailed instructions.

#### Conventions in babymaker

In order to homogenize the code and know what to expect, we try to follow these conventions in the  development
of `babymaker`:

 * **Branch names** use **all lower case letters**. If words must be separated, use an underscore, e.g. `met_phi`
 * **File names** use **all lower case letters**. If words must be separated, use an underscore, e.g. `lepton_tools.cc`
 * **Function names** follow the standard **CMSSW convention**, that is, first word all lower case, and first letter 
 of subsequent words in upper case. e.g. `bmaker_full::writeFatJets`
 * **Product names** (e.g. `"slimmedElectrons"`) are **only defined in `bmaker_full::analize` or in 
 `babymaker/bmaker/python/bmaker_full_cfg.py`**. 
 * As much as possible, **physics definitions go in the corresponding `src/*_tools.cc` file**, e.g. lepton ID goes in
 `src/lepton_tools.cc`. They should not be part of `plugins/bmaker_full.cc` so that when/if we move to having various 
 baby definitions in parallel, for which the code is setup, all babies would use common definitions.
