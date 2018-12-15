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
## => if doJEC = False, DeepCSV discriminator will not be included
doJEC = True

# if doJEC: jets_label = "updatedPatJetsTransientCorrectedUpdatedJEC"
if doJEC: jets_label = "updatedPatJetsUpdatedJEC"
else: jets_label = "slimmedJets"

# to apply JECs with txt files in babymaker, 
# prefix jecLabel with "onthefly_", e.g. onthefly_Spring16_25nsV6_MC
# systematics will also be calculated using this tag, even if JECs are not re-applied
# N.B. JECs change in the middle of RunF, thereby the Run2016F1 vs Run2016F2 distinction
jecLabel = 'onthefly_Spring16_23Sep2016V2_MC'
if ("Run2016B" in outName) or ("Run2016C" in outName) or ("Run2016D" in outName): 
  jecLabel = 'Summer16_23Sep2016BCDV3_DATA'
elif ("Run2016E" in outName) or ("Run2016F1" in outName):
  jecLabel = 'Summer16_23Sep2016EFV3_DATA'
elif ("Run2016F2" in outName) or ("Run2016G" in outName):
  jecLabel = 'Summer16_23Sep2016GV3_DATA'
elif ("Run2016H" in outName): 
  jecLabel = 'Summer16_23Sep2016HV3_DATA'
elif "RunIISpring16MiniAOD" in outName:
  jecLabel = 'Spring16_23Sep2016V2_MC' # for ICHEP MC against re-reco data
elif "RunIISummer16MiniAOD" in outName:
  jecLabel = 'Summer16_23Sep2016V3_MC'
elif "RunIIFall17MiniAODv2" in outName:
  jecLabel = 'Fall17_17Nov2017_V32_MC'
elif "Run2017" in outName:
  jecLabel = 'Summer16_23Sep2016GV3_DATA'

# because FastSim naming for JECs variables inside db and txt files is really truly messed up...
if fastsim: jecLabel = 'Spring16_25nsFastSimV1_MC'
jecCorrLabel = jecLabel
if fastsim: jecCorrLabel = 'Spring16_25nsFastSimMC_V1'
jecBabyLabel = jecLabel
if fastsim: 
  if (doJEC): jecBabyLabel = 'Spring16_FastSimV1_MC'
  else: jecBabyLabel = 'onthefly_Spring16_FastSimV1_MC'


if "Run201" in outName:
    isData = True
    # These only used for the official application of JECs
    globalTag = "80X_dataRun2_2016SeptRepro_v6"
    processRECO = "RECO"
else:
    isData = False
    # These only used for the official application of JECs
    globalTag = "80X_mcRun2_asymptotic_2016_miniAODv2"
    if "RunIISummer16MiniAOD" in outName: globalTag = "80X_mcRun2_asymptotic_2016_TrancheIV_v7"
    elif "RunIIFall17MiniAODv2" in outName: globalTag = "94X_mc2017_realistic_v14"
    processRECO = "PAT"

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
                                    jec = cms.string(jecBabyLabel),
                                    met = cms.InputTag("slimmedMETsModifiedMET"),
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
baddetEcallist = cms.vuint32(
    [872439604,872422825,872420274,872423218,
     872423215,872416066,872435036,872439336,
     872420273,872436907,872420147,872439731,
     872436657,872420397,872439732,872439339,
     872439603,872422436,872439861,872437051,
     872437052,872420649,872422436,872421950,
     872437185,872422564,872421566,872421695,
     872421955,872421567,872437184,872421951,
     872421694,872437056,872437057,872437313]
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
    jecLabel = 'Fall17_17Nov2017_V32_94X_MC'
    jecCorrLabel = 'Fall17_17Nov2017_V32_94X_MC'
    process.jec = cms.ESSource("PoolDBESSource",CondDBSetup,
                               connect = cms.string('sqlite_fip:babymaker/data/jec/'+jecLabel+'.db'),
                               toGet   = cms.VPSet(
                                   cms.PSet(
                                       record = cms.string("JetCorrectionsRecord"),
                                       tag    = cms.string("JetCorrectorParametersCollection_"+jecCorrLabel+"_AK4PFchs"),
                                       label  = cms.untracked.string("AK4PFchs")
                                   )
                )
    )
    process.es_prefer_jec = cms.ESPrefer("PoolDBESSource","jec")
    ###### Applying JECs and including deepCSV info
    ## From https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#CorrPatJets
    from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
    updateJetCollection(
      process,
      jetSource = cms.InputTag('slimmedJets'),
      jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual']), 'None'),
      # pvSource = cms.InputTag('offlineSlimmedPrimaryVertices'), # doesn't work :(
      # svSource = cms.InputTag('slimmedSecondaryVertices'),
      # btagDiscriminators = [  
      #   'pfDeepFlavourJetTags:probb', 
      #   'pfDeepFlavourJetTags:probbb',
      #   'pfDeepFlavourJetTags:problepb',
      #   'pfDeepFlavourJetTags:probc',
      #   'pfDeepFlavourJetTags:probuds',
      #   'pfDeepFlavourJetTags:probg'
      #   ],
      postfix = 'UpdatedJEC',
    )

    ###### Apply new JECs to MET
    ## From https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription
    from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
    ## If you only want to re-correct and get the proper uncertainties, no reclustering
    runMetCorAndUncFromMiniAOD(process,
                               isData = isData,
                               fixEE2017 = True,
                               fixEE2017Params = {'userawPt': True, 'ptThreshold':50.0, 'minEtaThreshold':2.65, 'maxEtaThreshold':3.139},
                               postfix = "ModifiedMET"
    )

# L1 prefiring issue
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/L1ECALPrefiringWeightRecipe 
prefire_dataEra = "2017BtoF"
if "RunIISummer16MiniAOD" in outName: prefire_dataEra = "2016BtoH"
process.prefiringweight = cms.EDProducer("L1ECALPrefiringWeightProducer",
                                          ThePhotons = cms.InputTag("slimmedPhotons"),
                                          TheJets = cms.InputTag("slimmedJets"),
                                          L1Maps = cms.string("data/L1Prefire/L1PrefiringMaps_new.root"), # update this line with the location of this file
                                          DataEra = cms.string(prefire_dataEra),
                                          UseJetEMPt = cms.bool(False), #can be set to true to use jet prefiring maps parametrized vs pt(em) instead of pt
                                          PrefiringRateSystematicUncty = cms.double(0.2) #Minimum relative prefiring uncty per object
                                          )

# putting EDProducers and EDFilters in a task is the new way to run unscheduled since 90X
process.myTask = cms.Task(process.prefiringweight, 
                          process.ecalBadCalibReducedMINIAODFilter, 
                          process.patJetCorrFactorsUpdatedJEC, 
                          process.updatedPatJetsUpdatedJEC
                          )

# printing stuff about the event
# process.add_(cms.Service("Tracer"))
# process.add_(cms.Service("ProductRegistryDumper"))
# Include process.dump* in the path to have all the event ojects printed out
process.dump=cms.EDAnalyzer('EventContentAnalyzer')

process.p = cms.Path(process.fullPatMetSequenceModifiedMET*process.baby_full)
process.p.associate(process.myTask)