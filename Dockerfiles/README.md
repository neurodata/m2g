### Docker Instructions

The [neurodata/ndmg](https://hub.docker.com/r/neurodata/ndmg/) Docker container enables users to run end-to-end connectome estimation on structural MRI right from container launch. The pipeline requires that data be organized in accordance with the [BIDS](http://bids.neuroimaging.io) spec. If the data you wish to process is available on S3 you simply need to provide your s3 credentials at build time and the pipeline will auto-retrieve your data for processing.


**To get your container ready to run just follow these steps:**

*(A) I do not wish to use S3*:

- In your terminal, type:
```{bash}
$ docker pull neurodata/ndmg
```

*(B) I wish to use S3*:

- Add your secret key/access id to a file called `credentials.csv` in this directory on your local machine. A dummy file has been provided to make the format we expect clear. (This is how AWS provides credentials)
- In your terminal, navigate to this directory and type:
```{bash}
$ docker build -t <yourhandle>/ndmg .
```


**Now we're ready to launch our instances and process some data!**

Like a normal docker container, you can startup your container with a single line. Let's assume I am running this and I wish to use S3, so my container is called `gkiar/ndmg`. If you don't want to use S3, you can replace `gkiar` with `neurodata` and ignore the S3 related flags for the rest of the tutorial.

I can start my container with:
```{bash}
$ docker run -ti gkiar/ndmg
usage: ndmg_bids [-h]
                 [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
                 [--bucket BUCKET] [--remote_path REMOTE_PATH]
                 bids_dir output_dir {participant}
ndmg_bids: error: too few arguments
```

We should've noticed that I got an error back suggesting that I didn't properly provide information to our container. Let's try again, with the help flag:
```{bash}
$ docker run -ti neurodata/ndmg:v4 -h

usage: ndmg_bids [-h]
                 [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
                 [--bucket BUCKET] [--remote_path REMOTE_PATH]
                 bids_dir output_dir {participant}

This is an end-to-end connectome estimation pipeline from sMRI and DTI images

positional arguments:
  bids_dir              The directory with the input dataset formatted
                        according to the BIDS standard.
  output_dir            The directory where the output files should be stored.
                        If you are running group level analysis this folder
                        should be prepopulated with the results of the
                        participant level analysis.
  {participant}         Level of the analysis that will be performed. Multiple
                        participant level analyses can be run independently
                        (in parallel) using the same output_dir.

optional arguments:
  -h, --help            show this help message and exit
  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                        The label(s) of the participant(s) that should be
                        analyzed. The label corresponds to
                        sub-<participant_label> from the BIDS spec (so it does
                        not include "sub-"). If this parameter is not provided
                        all subjects should be analyzed. Multiple participants
                        can be specified with a space separated list.
  --bucket BUCKET       The name of an S3 bucket which holds BIDS organized
                        data. You must have built your bucket with credentials
                        to the S3 bucket you wish to access.
  --remote_path REMOTE_PATH
                        The path to the data on your S3 bucket. The data will
                        be downloaded to the provided bids_dir on your
                        machine.
```

Cool! That taught us some stuff. So now for the last unintuitive piece of instruction and then just echoing back commands I'm sure you could've figured out from here: in order to share data between our container and the rest of our machine, we need to mount a volume. Docker does this with the `-v` flag. Docker expects its input formatted as: `-v path/to/local/data:/path/in/container`. We'll do this when we launch our container, as well as give it a helpful name so we can locate it later on. Finally:
```{bash}
docker run -ti --name ndmg_test -v ./data:${HOME}/data neurodata/ndmg ${HOME}/data/ ${HOME}/data/outputs participant -p 01 -b mybucket -r path/on/bucket/
```
