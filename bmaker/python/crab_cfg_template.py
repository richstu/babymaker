## Template file for CRAB submission. The script generate_crab_config.py 
## replaces the following two lines with the appropriate values
## Do not edit manually!
dataset = 'DATASETNAME'
nevents = NEVENTS

# CRAB3 task names can no longer be greater than 100 characters; need to shorten task name
taskname = dataset[1:].replace('/','__')
taskname = taskname.replace('RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2','80XMiniAODv2')
taskname = taskname.replace('RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3','RunIISummer16MiniAODv3')
taskname = taskname.replace('RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14','RunIIFall17MiniAODv2')

taskname = taskname.replace('RunIISummer16MiniAODv3-PUSummer16v3Fast_94X_mcRun2_asymptotic_v3-v1','RunIISummer16MiniAODv3Fast')
taskname = taskname.replace('RunIIFall17MiniAODv2-PUFall17Fast_94X_mc2017_realistic_v15-v1','RunIIFall17MiniAODv2Fast')
taskname = taskname.replace('RunIIFall17MiniAODv2-PUFall17Fast_lhe_94X_mc2017_realistic_v15-v1','RunIIFall17MiniAODv2Fast')
taskname = taskname.replace('RunIIFall17MiniAODv2-PUFall17Fast_pilot_94X_mc2017_realistic_v15-v3','RunIIFall17MiniAODv2Fast')
taskname = taskname.replace('RunIIFall17MiniAODv2-PUFall17Fast_pilot_94X_mc2017_realistic_v15_ext1-v1','RunIIAutumn18MiniAODFastFake')
taskname = taskname.replace('RunIIFall17MiniAODv2-PUFall17Fast_94X_mc2017_realistic_v15_ext1-v1','RunIIAutumn18MiniAODFastFake')
taskname = taskname.replace(':','___')

if(len(taskname)>100): taskname = taskname[0:99]

datasetID = dataset.replace('/','',1).replace('/', '_', 1)
datasetID = datasetID[0:datasetID.find('/')]

from WMCore.Configuration import Configuration
config = Configuration()

config.section_("General")
config.General.requestName = taskname
config.General.workArea = 'out_crab'
config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'babymaker/bmaker/python/bmaker_full_cfg.py'
config.JobType.disableAutomaticOutputCollection = True
# config.JobType.sendExternalFolder = True #DAK8
config.JobType.outputFiles = ['fullbaby_' + datasetID + '.root']
config.JobType.pyCfgParams = ['nEventsSample=' + str(nevents), 'outputFile=fullbaby_' + datasetID + '.root']

config.section_("Data")
config.Data.inputDataset = dataset
config.Data.inputDBS = 'global'
# config.Data.ignoreLocality = True
config.Data.allowNonValidInputDataset = True
if "Run201" in taskname:
    config.Data.splitting = 'LumiBased'
    config.Data.unitsPerJob = 50
    config.Data.lumiMask = 'babymaker/data/json/golden_Cert_314472-325175_13TeV_PromptReco_Collisions18.json' 
else:
    config.Data.splitting = 'FileBased'
    config.Data.unitsPerJob = 5

config.Data.publication = False # used to be True for cfA production
# config.Data.publishDBS = 'phys03'

config.section_("Site")
config.Site.storageSite = 'T2_US_UCSD'
#config.Site.storageSite = 'T3_US_UCSB'
# config.Site.whitelist = ['T2_US_Caltech','T2_US_Florida', 'T2_US_MIT', 'T2_US_Nebraska', 'T2_US_Purdue', 'T2_US_UCSD', 'T2_US_Wisconsin', 'T1_US_FNAL','T2_US_MIT']
#config.Site.blacklist = ['T2_US_Vanderbilt']
# you may want to uncomment this line and force jobs to run in the US
# only a few datasets (mostly very new ones) will not be accessible
