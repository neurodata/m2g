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
Error: Missing input, output directory or subject id.
 Try 'ndmg_bids -h' for help
```

We should've noticed that I got an error back suggesting that I didn't properly provide information to our container. Let's try again, with the help flag:
```{bash}
$ docker run -ti gkiar/ndmg -h

usage: ndmg_bids [-h] [-i BIDS_DIR] [-o OUTPUT_DIR] [-p PARTICIPANT_LABEL]
                 [-s SESSION_LABEL] [-b BUCKET] [-r REMOTE_PATH]

This is an end-to-end connectome estimation pipeline from sMRI and DTI images

optional arguments:
  -h, --help            show this help message and exit
  -i BIDS_DIR, --bids-dir BIDS_DIR
                        Base directory for input data
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Base directory to store derivaties
  -p PARTICIPANT_LABEL, --participant-label PARTICIPANT_LABEL
                        Subject ID to be analyzed
  -s SESSION_LABEL, --session-label SESSION_LABEL
                        Session ID to be analyzed (if multiple exist)
  -b BUCKET, --bucket BUCKET
                        Name of S3 bucket containing data
  -r REMOTE_PATH, --remote-path REMOTE_PATH
                        Path of data on bucket
```

Cool! That taught us some stuff. So now for the last unintuitive piece of instruction and then just echoing back commands I'm sure you could've figured out from here: in order to share data between our container and the rest of our machine, we need to mount a volume. Docker does this with the `-v` flag. Docker expects its input formatted as: `-v path/to/local/data:/path/in/container`. We'll do this when we launch our container, as well as give it a helpful name so we can locate it later on. Finally:
```{bash}
docker run -ti --name ndmg_test -v ./data:${HOME}/data neurodata/ndmg -i ${HOME}/data/ -o ${HOME}/data/outputs -p 01 -s 01 -b mybucket -r path/on/bucket/
```
