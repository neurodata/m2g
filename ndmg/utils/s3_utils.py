import subprocess
from configparser import ConfigParser
import os
import sys

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


def s3_get_data(bucket, remote, local, public=False, force=False):
    """Given and s3 directory, copies files/subdirectories in that directory to local
    
    Parameters
    ----------
    bucket : str
        s3 bucket you are accessing data from
    remote : str
        The path to the data on your S3 bucket. The data will be
        downloaded to the provided bids_dir on your machine.
    local : str
        Local input directory where you want the files copied to
    public : bool, optional
        Whether or not the data you are accessing is public, if False s3 credentials are used, by default False
    force : bool, optional
        Whether to overwrite the local directory containing the s3 files if it already exists, by default False
    """
    

    # TODO : use boto3 for this
    if os.path.exists(local) and not force:
        print("Local directory already exists. Not pulling s3 data.")
        return  # TODO: make sure this doesn't append None a bunch of times to a list in a loop on this function
    if not public:
        # get client with credentials if they exist
        try:
            client = s3_client(service="s3")
        except:
            client = boto3.client("s3")

        bkts = [bk["Name"] for bk in client.list_buckets()["Buckets"]]
        if bucket not in bkts:
            sys.exit(
                "Error: could not locate bucket. Available buckets: " + ", ".join(bkts)
            )

        cmd = "aws s3 cp --exclude 'ndmg_*' --recursive s3://{}/{}/ {};\nwait".format(
            bucket, remote, local
        )
    if public:
        cmd += " --no-sign-request --region=us-east-1;\nwait"

    print("Calling {} to get data from S3 ...".format(cmd))
    out = subprocess.check_output("mkdir -p {}".format(local), shell=True)
    out = subprocess.check_output(cmd, shell=True)
    out = subprocess.check_output(
        'echo "\n\n\n\n\n\n\nDATA ARRIVED\n\n\n\n\n\n" {}'.format(local), shell=True
    )
    print(out)


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
    # TODO : use boto3 for this instead
    cmd = (
        'aws s3 cp --exclude "tmp/*" {} s3://{}/{}/{}/{}/ --recursive --acl public-read'
    )
    dataset = remote.split("/")[0]
    rest_of_path_list = remote.split("/")[1:]
    rest_of_path = os.path.join(*rest_of_path_list)
    cmd = cmd.format(outDir, bucket, dataset, modifier, rest_of_path)
    if not creds:
        print("Note: no credentials provided, may fail to push big files.")
        cmd += " --no-sign-request"
    print("Pushing results to S3: {}".format(cmd))
    subprocess.check_output(cmd, shell=True)
