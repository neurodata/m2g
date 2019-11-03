"""
ndmg.utils.cloud_utils
~~~~~~~~~~~~~~~~~~~~~~

Contains utility functions for working on the cloud with AWS.
"""

# standard library imports
import subprocess
from configparser import ConfigParser
import os
import sys

# package imports
import boto3


def get_credentials():
    """Searches for and returns AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

    Returns
    -------
    tuple
        Two strings inside of a tuple, (Access_key, Secret_access_key)

    Raises
    ------
    AttributeError
        No AWS credentials are found
    """
    # add option to pass profile name
    try:
        config = ConfigParser()
        config.read(os.getenv("HOME") + "/.aws/credentials")
        return (
            config.get("default", "aws_access_key_id"),
            config.get("default", "aws_secret_access_key"),
        )
    except:
        ACCESS = os.getenv("AWS_ACCESS_KEY_ID")
        SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
    if not ACCESS and SECRET:
        raise AttributeError("No AWS credentials found.")
    return (ACCESS, SECRET)


def s3_client(service="s3"):
    """
    create an s3 client.

    Parameters
    ----------
    service : str
        Type of service.

    Returns
    -------
    boto3.client
        client with proper credentials.
    """

    try:
        ACCESS, SECRET = get_credentials()
    except AttributeError:
        return boto3.client(service)
    return boto3.client(service, aws_access_key_id=ACCESS, aws_secret_access_key=SECRET)


def get_matching_s3_objects(bucket, prefix="", suffix=""):
    """
    Generate objects in an S3 bucket.

    Parameters
    ----------
    bucket : str
        Name of the s3 bucket.
    prefix : str, optional
        Only fetch objects whose key starts with this prefix, by default ''
    suffix : str, optional
        Only fetch objects whose keys end with this suffix, by default ''
    """
    s3 = s3_client(service="s3")
    kwargs = {"Bucket": bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs["Prefix"] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)

        try:
            contents = resp["Contents"]
        except KeyError:
            print("No contents found.")
            return

        for obj in contents:
            key = obj["Key"]
            if key.startswith(prefix) and key.endswith(suffix):
                yield key

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs["ContinuationToken"] = resp["NextContinuationToken"]
        except KeyError:
            break


def s3_get_data(bucket, remote, local, info='', public=False, force=False):
    """Given and s3 directory, copies files/subdirectories in that directory to local

    Parameters
    ----------
    bucket : str
        s3 bucket you are accessing data from
    remote : str
        The path to the data on your S3 bucket. The data will be
        downloaded to the provided bids_dir on your machine.
    local : list
        Local input directory where you want the files copied to and subject/session info [input, sub-#/ses-#]
    info : str, optional
        Relevant subject and session information in the form of sub-#/ses-#
    public : bool, optional
        Whether or not the data you are accessing is public, if False s3 credentials are used, by default False
    force : bool, optional
        Whether to overwrite the local directory containing the s3 files if it already exists, by default False
    """

    if os.path.exists(os.path.join(local,info)) and not force:
        if os.listdir(os.path.join(local,info)):
            print(f'Local directory: {os.path.join(local,info)} already exists. Not pulling s3 data. Delete contents to re-download data.')
            return  # TODO: make sure this doesn't append None a bunch of times to a list in a loop on this function
        else:
            pass
    
    if not public:
        # get client with credentials if they exist
        try:
            client = s3_client(service="s3")
        except:
            client = boto3.client("s3")
    else:
        client = boto3.client("s3")
    
    # check that bucket exists
    bkts = [bk["Name"] for bk in client.list_buckets()["Buckets"]]
    if bucket not in bkts:
        sys.exit(
            "Error: could not locate bucket. Available buckets: " + ", ".join(bkts)
        )

    # go through all folders inside of remote directory and download relevant files
    s3 = boto3.resource('s3')
    buck = s3.Bucket(bucket)
    for obj in buck.objects.filter(Prefix=f'{remote}'):
        bdir,data = os.path.split(obj.key)
        print(os.path.join(local,*bdir.split('/')[-3:]))
        # Make directory for data if it doesn't exist
        if not os.path.exists(os.path.join(local,*bdir.split('/')[-3:])):
            os.makedirs(os.path.join(local,*bdir.split('/')[-3:]))
        print(f'Downloading {bdir}/{data} from {bucket} s3 bucket...')
        # Download file 
        client.download_file(bucket,f'{bdir}/{data}',f'{os.path.join(local,*bdir.split("/")[-3:])}/{data}')
        if os.path.exists(f'{os.path.join(local,*bdir.split("/")[-3:])}/{data}'):
            print('Success!')




def s3_push_data(bucket, remote, outDir, modifier, creds=True, debug=True):
    """Pushes data to a specified S3 bucket

    Parameters
    ----------
    bucket : str
        s3 bucket you are pushing files to
    remote : str
        The path to the directory on your S3 bucket containing the data used in the pipeline, the string in 'modifier' will be put after the
        first directory specified in the path as its own directory (/remote[0]/modifier/remote[1]/...)
    outDir : str
        Path of local directory being pushed to the s3 bucket
    modifier : str
        Name of the folder on s3 to push to. If empty, push to a folder with ndmg's version number. Default is ""
    creds : bool, optional
        Whether s3 credentials are being provided, may fail to push big files if False, by default True
    debug : bool, optional
        Whether to not to push intermediate files created by the pipeline, by default True
    """

    if creds:
        # get client with credentials if they exist
        try:
            client = s3_client(service="s3")
        except:
            client = boto3.client("s3")
    else:
        client = boto3.client("s3")
    
    # check that bucket exists
    bkts = [bk["Name"] for bk in client.list_buckets()["Buckets"]]
    if bucket not in bkts:
        sys.exit(
            "Error: could not locate bucket. Available buckets: " + ", ".join(bkts)
        )

    # List all files and upload
    for r, d, f in os.walk(outDir):
        for file in f:
            if not 'tmp/' in r: # exclude things in the tmp/ folder
                print(f'Uploading: {os.path.join(r, file)}')
                d = r.replace(os.path.join('/',*outDir.split('/')[:-2]),'') #remove everything before /sub-*
                client.upload_file(
                    os.path.join(r, file), bucket, f'{remote}/{modifier}{os.path.join(d,file)}',
                    ExtraArgs={'ACL':'public-read'}
                    )
