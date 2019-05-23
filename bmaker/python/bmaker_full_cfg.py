###########################################################
### Configuration file to make full babies from miniAOD
###########################################################
import math, sys
from   os import environ
from   os.path import exists, join, basename

def findFileInPath(theFile):
    for s in environ["CMSSW_SEARCH_PATH"].split(":"):
        attempt = join(s,theFile)
        if exists(attempt):
            return attempt
    print "BABYMAKER: Could not find file "+theFile+". Not pre-applying JSON"
    return None

###### Input parameters parsing 
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('analysis')
options.register('nEventsSample',
                 100,
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.int,
                 "Total number of events in dataset for event weight calculation.")
options.register('nEvents',
                 100,
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.int,
                 "Number of events to run over.")
options.register('json',
                 'babymaker/data/json/golden_Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON_NoL1T.txt', 
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "Path to json starting with babymaker/...")
options.register('condorSubTime',
                 '000000_000000',
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "Timestamp from condor submission")
options.parseArguments()
outName = options.outputFile
if outName == "output.root": # output filename not set
    rootfile = basename(options.inputFiles[0])
    outName = "fullbaby_"+rootfile.replace("file:","")

doSystematics = True
if "FSPremix" in outName or "Fast" in outName: fastsim = True
else: fastsim = False

    
## JECs must be undone and reapplied when rerunning b-tagging
doJEC = True 
doDeepFlavour = False
if doJEC: 
    # met_label = "slimmedMETs" #fixme
    met_label = "slimmedMETsModifiedMET"
    if doDeepFlavour:
        jets_label = "selectedUpdatedPatJetsNewDFTraining"
    else:
        jets_label = "updatedPatJetsUpdatedJEC"
else: 
    jets_label = "slimmedJets"
    met_label = "slimmedMETs"

# to apply JECs with txt files in babymaker, 
# prefix jecDBFile with "onthefly_", e.g. onthefly_Spring16_25nsV6_MC
# systematics will also be calculated using this tag, even if JECs are not re-applied
# N.B. B-tagging WPs are also selected based on this label
jecDBFile = 'onthefly_Spring16_23Sep2016V2_MC'
jecLevels = ['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual']
if "Run201" in outName:
    isData = True
    processRECO = "RECO"
    if "Run2016" in outName:
      globalTag = '94X_dataRun2_v10'
      jecDBFile  = 'Summer16_07Aug2017All_V11_DATA'
    if "Run2017" in outName:
      globalTag = '102X_dataRun2_v8'
      jecDBFile  = 'Fall17_17Nov2017_V32_102X_DATA'
    if "Run2018" in outName:
      globalTag = '102X_dataRun2_v8'
      jecDBFile  = 'Autumn18_RunABCD_V8_DATA'
else:
    isData = False
    processRECO = "PAT"
    if "RunIISummer16" in outName:
      globalTag = '94X_mcRun2_asymptotic_v3'
      jecDBFile  = 'Summer16_07Aug2017_V11_MC'
    if "RunIIFall17" in outName:
      globalTag = '94X_mc2017_realistic_v14'
      jecDBFile  = 'Fall17_17Nov2017_V32_102X_MC'
    if "RunIIAutumn18" in outName:
      globalTag = '102X_upgrade2018_realistic_v15'
      jecDBFile  = 'Autumn18_V8_MC'

# some special gymnastics around the FastSim JEC file naming...
jecTXTFile = jecDBFile
if fastsim: 
  jecLevels = ['L1FastJet', 'L2Relative', 'L3Absolute']
  if "RunIIFall17" in outName:
    jecDBFile = 'Fall17_FastSimV1_MC'
    jecTXTFile = 'Fall17_FastSimV1_MC'
  elif "RunIIAutumn18" in outName:
    jecDBFile = 'Autumn18_FastSimV1_MC'
    jecTXTFile = 'Autumn18_FastSimV1_MC'
  else:
    jecDBFile = 'Summer16_25nsFastSimMC_V1'
    jecTXTFile = 'Spring16_FastSimV1_MC'
  # to instruct babymaker to apply JECs instead via the txt files, add 'onthefly_'
  if not doJEC:
    jecTXTFile = 'onthefly_'+jecTXTFile

###### Defining Baby process, input and output files 
process = cms.Process("Baby")
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(options.inputFiles)
)
if isData: # Processing only lumis in JSON
    import FWCore.PythonUtilities.LumiList as LumiList
    jsonfile = findFileInPath(options.json)
    process.source.lumisToProcess = LumiList.LumiList(filename = jsonfile).getVLuminosityBlockRange()
    doSystematics = False

process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

####### Setting global tag - using DB for now
## From https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JecGlobalTag
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = globalTag

# DAK8
# needed for DeepAK8
# process.TransientTrackBuilderESProducer = cms.ESProducer("TransientTrackBuilderESProducer",
#     ComponentName=cms.string('TransientTrackBuilder')
# )

process.baby_full = cms.EDAnalyzer('bmaker_full',
                                    condor_subtime = cms.string(options.condorSubTime),
                                    outputFile = cms.string(outName),
                                    inputFiles = cms.vstring(options.inputFiles),
                                    json = cms.string(options.json),
                                    jec = cms.string(jecTXTFile),
                                    met = cms.InputTag(met_label),
                                    met_nohf = cms.InputTag("slimmedMETsNoHF"),
                                    jets = cms.InputTag(jets_label),
                                    nEventsSample = cms.uint32(options.nEventsSample),
                                    doMetRebalancing = cms.bool(True),
                                    doSystematics = cms.bool(doSystematics),
                                    addBTagWeights = cms.bool(True),
                                    isFastSim = cms.bool(fastsim),
                                    debugMode = cms.bool(False)
)

###### Setting up number of events, and reporing frequency 
process.load("FWCore.MessageService.MessageLogger_cfi")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.nEvents) )
process.MessageLogger.cerr.FwkReport.reportEvery = 100000

# ECAL bad calibration filter update for 2017 and 2018 only
if "RunIISummer16" not in outName and "Run2016" not in outName:
    baddetEcallist = cms.vuint32(
      [872439604,872422825,872420274,872423218,
       872423215,872416066,872435036,872439336,
       872420273,872436907,872420147,872439731,
       872436657,872420397,872439732,872439339,
       872439603,872422436,872439861,872437051,
       872437052,872420649,872421950,872437185, 
       872422564,872421566,872421695,872421955,
       872421567,872437184,872421951,872421694, 
       872437056,872437057,872437313,872438182,
       872438951,872439990,872439864,872439609,
       872437181,872437182,872437053,872436794,
       872436667,872436536,872421541,872421413, 
       872421414,872421031,872423083,872421439]
       )
    process.ecalBadCalibReducedMINIAODFilter = cms.EDFilter(
      "EcalBadCalibFilter",
      EcalRecHitSource = cms.InputTag("reducedEgamma:reducedEERecHits"),
      ecalMinEt        = cms.double(50.),
      baddetEcal    = baddetEcallist, 
      taggingMode = cms.bool(True),
      debug = cms.bool(False)
      )

if doJEC:
    ###### Setting sqlite file for the JECs that are in newer global tags 
    ## From https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JecSqliteFile
    process.load("CondCore.DBCommon.CondDBCommon_cfi")
    from CondCore.DBCommon.CondDBSetup_cfi import CondDBSetup
    process.jec = cms.ESSource("PoolDBESSource",CondDBSetup,
                               connect = cms.string('sqlite_fip:babymaker/data/jec/'+jecDBFile+'.db'),
                               toGet   = cms.VPSet(
                                   cms.PSet(
                                       record = cms.string("JetCorrectionsRecord"),
                                       tag    = cms.string("JetCorrectorParametersCollection_"+jecDBFile+"_AK4PFchs"),
                                       label  = cms.untracked.string("AK4PFchs")
                                   )
                )
    )
    process.es_prefer_jec = cms.ESPrefer("PoolDBESSource","jec")
    ###### Applying JECs and including deepCSV info
    ## From https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#CorrPatJets
    from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
    if doDeepFlavour:
        updateJetCollection(
          process,
          jetSource = cms.InputTag('slimmedJets'),
          jetCorrections = ('AK4PFchs', cms.vstring(jecLevels), 'None'),
          pvSource = cms.InputTag('offlineSlimmedPrimaryVertices'),
          svSource = cms.InputTag('slimmedSecondaryVertices'),
          btagDiscriminators = [  
            'pfDeepFlavourJetTags:probb', 
            'pfDeepFlavourJetTags:probbb',
            'pfDeepFlavourJetTags:problepb',
            'pfDeepFlavourJetTags:probc',
            'pfDeepFlavourJetTags:probuds',
            'pfDeepFlavourJetTags:probg'
            ],
          postfix = 'NewDFTraining',
        )
    else:
        updateJetCollection(
          process,
          jetSource = cms.InputTag('slimmedJets'),
          jetCorrections = ('AK4PFchs', cms.vstring(jecLevels), 'None'),
          postfix = 'UpdatedJEC',
        )
    ###### Apply new JECs to MET
    ## From https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription
    from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD #fixme
    if ("RunIIFall17" in outName) or ("Run2017" in outName):
      runMetCorAndUncFromMiniAOD(process,
                                 isData = isData,
                                 fixEE2017 = True,
                                 fixEE2017Params = {'userawPt': True, 'ptThreshold':50.0, 'minEtaThreshold':2.65, 'maxEtaThreshold':3.139},
                                 postfix = "ModifiedMET"
      )
    else:
      runMetCorAndUncFromMiniAOD(process,
                                 isData = isData,
                                 postfix = "ModifiedMET"
      )
# L1 prefiring issue
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/L1ECALPrefiringWeightRecipe 
if "RunIISummer16" in outName or "RunIIFall17" in outName:
  prefire_dataEra = "2017BtoF"
  if "RunIISummer16" in outName: prefire_dataEra = "2016BtoH"
  prefire_file = 'CMSSW_10_2_6/src/babymaker/data/L1Prefire/L1PrefiringMaps_new.root'
  if 'babymaker' in environ['PWD']:
    prefire_file = 'data/L1Prefire/L1PrefiringMaps_new.root'
  process.prefiringweight = cms.EDProducer("L1ECALPrefiringWeightProducer",
                                            ThePhotons = cms.InputTag("slimmedPhotons"),
                                            TheJets = cms.InputTag("slimmedJets"),
                                            L1Maps = cms.string(prefire_file), # update this line with the location of this file
                                            DataEra = cms.string(prefire_dataEra),
                                            UseJetEMPt = cms.bool(False), #can be set to true to use jet prefiring maps parametrized vs pt(em) instead of pt
                                            PrefiringRateSystematicUncty = cms.double(0.2) #Minimum relative prefiring uncty per object
                                            )

# printing stuff about the event
# process.add_(cms.Service("Tracer"))
# process.add_(cms.Service("ProductRegistryDumper"))
# Include process.dump* in the path to have all the event ojects printed out
process.dump=cms.EDAnalyzer('EventContentAnalyzer')

# putting EDProducers and EDFilters in a task is the new way to run unscheduled since 90X
process.tsk = cms.Task()
for mod in process.producers_().itervalues():
    process.tsk.add(mod)
for mod in process.filters_().itervalues():
    process.tsk.add(mod)

process.p = cms.Path(
  process.baby_full,
    process.tsk
)
