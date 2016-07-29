### Docker Instructions

The [neurodata/ndmg](https://hub.docker.com/r/neurodata/ndmg/) Docker container enables users to run end-to-end connectome estimation on structural MRI right from container launch. The pipeline requires that data be organized in accordance with the [BIDS](http://bids.neuroimaging.io) spec. If the data you wish to process is available on S3 you simply need to provide your s3 credentials at build time and the pipeline will auto-retrieve your data for processing.


**To get your container ready to run just follow these steps:**

*(A) I do not wish to use S3*:

- In your terminal, type `docker pull neurodata/ndmg`

*(B) I wish to use S3*:

- Add your secret key/access id to a file called `credentials.csv` in this directory on your local machine. A dummy file has been provided to make the format we expect clear. (This is how AWS provides credentials)
- In your terminal, navigate to this directory and type `docker build -t <yourhandle>/ndmg .`


**Now we're ready to launch our instances and process some data!**

Like a normal docker container, you can startup your container with a single line. Let's assume I am running this and I wish to use S3, so my container is called `gkiar/ndmg`.

I can start my container with: `docker run -ti gkiar/ndmg`.

We should've noticed that I got an error back suggesting that I didn't properly provide information to our container. Let's try again, with the help flag 

3. Use
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
                        Path to downloaded data

To run `ndmg_bids`:
```
docker run -ti --name ndmg -v /Users/gkiar/Downloads/ds114/:${HOME}/data neurodata/ndmg -i ${HOME}/data/ -o ${HOME}/data/outputs -p 02 -s test
```
