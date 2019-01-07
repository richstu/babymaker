# `genfiles`

Code for processing existing babies without CMSSW dependencies.

## Code setup

N.B. Until we update PyROOT on UCSB machines, the post-processing is setup to run in 8_0_16. To get started setup the release and compile genfiles *standalone*:

    cmsrel CMSSW_8_0_16
    cd CMSSW_8_0_16/src
    cmsenv
    git clone git@github.com:richstu/babymaker
    cd bmaker/genfiles/
    ./compile.sh

Note that running scram and compiling in the root `babymaker`
directory are unnecessary.

## Post-processing of ntuple production

Post-processing relies on the UCSB tier 3, so all ntuples must first
be copied to a folder like `/net/cmsX/cmsXr0/babymaker/babies/YYYY_MM_DD/mc/unprocessed/`. All commands
are issued from the `genfiles` directory for both MC and data.

If not done already, create a soft link from where the ntuples are to /net/cms2/cms2r0/babymaker/babies/YYYY_MM_DD, e.g.:

        cd /net/cms2/cms2r0/babymaker/babies/
        ln -s /net/cms29/cms29r0/babymaker/babies/YYYY_MM_DD YYYY_MM_DD
        ls -l

Before starting to process, make sure you have the permissions to rwx the files and folders. This will generally not be the case if you didn't do the copy to UCSB.

### Data

1. Combine datasets removing duplicates using 

        ./python/send_combine_data_datasets.py

    where you'll need to set the proper `infolder`, `outfolder`, `datasets`, and `jsonfile`, if not already set. This script sends
    combination jobs for groups of `run_files` runs.

2. Rename files to have the Run era in the filename such that it is easy to study effects dependent on the era once the babies are merged. Check the macro to see if any of the inputs need to be updated.

        ./python/rename_data_eras.py

3. Skim the combined dataset. Each skim requires one execution of
`python/send_skim_ntuples.py`. Make sure that the skim definition XXX is defined in `src/skim_ntuples.cxx`. If you change it, remember to compile(!):

        ./run/send_skim.sh /net/cms2/cms2r0/babymaker/babies/2018_12_17/data/unskimmed/ /net/cms2/cms2r0/babymaker/babies/2018_12_17/data/skim_XXX/ 40 XXX

    it's also possible to give the skim a name (try to make it such that it's as clear as possible to others what it contains) and then the last argument can just be a string like "met>100". Note that for more complex cuts this might not work because of special characters. If the cut was defined in `skim_ntuples.cxx`, please commit! Otherwise it would be impossible to tell what the skim contains later on.

4. Slim and merge the skimmed ntuples. To slim and merge a single skim: 

        ./python/send_slim_ntuples.py -i /net/cms2/cms2r0/babymaker/babies/2018_12_17/data/ -l txt/slim_rules/database.txt -k stdnj5

    If needed multiple skims can be slimmed with multiple slimming rules using `python/send_slim_ntuples.py`. The script takes the outer product of the requested slims and skims, so if one wanted the database and isrdata slims for both the stdnj5 and abcd skims produced in the last step, one would issue the command

        ./python/send_slim_ntuples.py -i /net/cms2/cms2r0/babymaker/babies/2018_12_17/data/ -l txt/slim_rules/database.txt txt/slim_rules/isrdata.txt -k stdnj5 abcd

    This will produce subdirectories `merged_database_stdnj5`, `merged_isrdata_stdnj5`, `merged_database_abcd`, and `merged_isrdata_abcd`.

5. Validate! One should minimally check that the number of root files stays the
same after skimming and that the number of events stays the same after
slimming and merging. The number of files can be checked with the
command

        python/count_root_files.py -f /net/cms2/cms2r0/babymaker/babies/YYYY_MM_DD/data

### MC

1. If one is processing signal scans, separate the mass points. This
is done with the script below after setting the proper `infolder` and `outfolder` and `outname`

        ./run/send_split_scan.py 


2. Renormalize the weights so that the cross section is kept constant. This is done in the groomer repository.

3. Validate `weight` by setting the proper `infolder`, `outfolder` in 

        ./python/validate_ntuples.py

    and running it. This script compares the sum of weights to an older production. The variable `weight`
    might have changed, so for instance when comparing Marmot and Capybara, the variables that would agree
    would be `weight/w_toppt/eff_trig` and `weight/w_isr/w_pu`

4. Follow steps 3 through 5 from [Data](#Data).

## [Not currently in use] Utility scripts and data caching 

There are two useful tools for running on the batch system:
`run/wrapper.sh` and `python/cache.py`. The former should be inserted
between `JobSubmit.csh` and the issued command for any batch job to
ensure the environment variables are set correctly during execution on
the Tier 3. For example, one might send

    JobSubmit.csh run/wrapper.sh echo "Hello world"

The latter script, `python/cache.py`, is a bit more general. It has
two main options, `--cache` and `--execute.` The `--execute` option is
followed by a command to be executed, much like `run/wrapper.sh`
is. The `--cache` option is followed by an arbitrary number of file
paths (possibly containing wildcards) to be cached in
`/scratch/babymaker`. If the provided file path already exists, it is
assumed to be an input file and simply copied to `/scratch/babymaker`;
if it does not exists, a temporary file is created in
`/scratch/babymaker` and then copied to the provided path when the
command given to `--execute` is done. Note that if any file in the
`--cache` list or any file appearing in the command line arguments for
`--execute` is modified by the executed script, the modified file is
copied back from the cache to the original location after
completion. As a simple example, it can be used as a replacement for
`run/wrapper.sh`:

    JobSubmit.csh python/cache.py --execute echo "Hello world"

The caching utility is mainly intended for skimming (it is used by
`python/send_skim_ntuples.py`) and other processing which performs a
large number of small write operations. For example, one can skim a
single file with

    python/cache.py --cache output_file.root --execute python/skim_ntuple.py baseline output_file.root /net/cmsX/cmsXr0/babymaker/babies/YYYY_MM_DD/data/unskimmed/*.root " --keep-existing"

There are two things one should observe in this example. First, the
file `output_file.root` can be used as an argument passed to
`python/skim_ntuple.py`; the caching script knows to automatically
replace it with the temporary file path created in
`/scratch/babymaker`. If one does not want this behavior, simply add a
`--fragile` and file paths will be left intact. Second, the
`--keep-existing` argument for `python/skim_ntuple.py` is quoted and
has a space before the dashes. This is necessary to prevent
python/cache.py from thinking the option was intended for itself and
instead have it forward the option to `python/skim_ntuple.py`.

The `python/cache.py` script does some crude management of the
available disk space. To prevent `/scratch/babymaker` from becoming
full, it accepts options specifying an absolute (`--abs_limit`) and
relative (`--rel_limit`) amount of disk space to leave empty. If the
cache is becoming too full, it will delete the least recently used
files in the cache until it has space for the new files. In the
extreme scenario where the cache is nearly full with recently used
files and being access by multiple processes, this can result in one
process deleting a cached file that is being read by
another. Hopefully this occurs very rarely, but the option
`--no-delete` is available to prevent files from being deleted from
the cache.
