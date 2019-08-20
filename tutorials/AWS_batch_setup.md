# ndmg on AWS Batch

To run ndmg on entire datasets, we use AWS Batch. <br>

## Requirements

- Docker
- An AWS account
- Your dataset on S3

## Overview

Our Batch pipeline works as follows.

1. Parse a BIDs-formatted dataset on s3 into a set of scans.
2. For each scan, create a JSON file containing its subject ID, session ID, and ndmg parameters.
3. For each JSON file, send a job to AWS.
4. AWS, upon receiving each job, creates a new EC2 instance, grabs our Docker image, and then runs a container using the arguments specified in the JSON.
5. The container then pulls the input data for that particular scan from S3, runs ndmg using that data, and upon completion, pushes the data back to S3 in the relevant location.

Steps 4 and 5 above occur in parallel -- meaning, if you have a dataset with 200 scans, there will be 200 EC2 instances running at the same time.

For arbitrarily large datasets, full runs generally take a little over an hour, at roughly \$.05/scan.

## Batch Setup : Console

This section shows you how to set up a batch environment such that you can easily run ndmg in parallel. For more in-depth documentation, see the [AWS official documentation](https://docs.aws.amazon.com/batch/index.html).

### Compute Environment

Your compute environment defines the compute resources AWS will use for its instances.

For ndmg, we recommend exclusively using `r5.large` instance types.

#### Initial Setup

**TODO : check if default roles can access s3 <br>**
Here, you define who can access the environment. We recommend using the default IAM roles.

1. Use Managed
2. Define a compute environment name
3. Define a service role. The default IAM is best.
4. Define an instance role. The default IAM (ecsInstanceRole) is best.
5. If you want to connect to your environments, you'll need a key-pair. This is optional; if you want to set this up, see the [official documentation](https://docs.aws.amazon.com/batch/latest/userguide/get-set-up-for-aws-batch.html#create-a-key-pair).

![initial compute](https://i.imgur.com/vEmEpuf.png)

#### Compute Resources

This section lets you define what resources your environment will use. You don't need to use any launch templates here; essentially the only thing necessary is to set the instance type to `r5.large`, and to raise the maximum vCPUs (in case you're running large datasets)

1. Set Allowed Instance types to `r5.large`
2. Set minimum vCPUs to 0

![Compute Resources](https://i.imgur.com/QZh4IlG.png)

You can leave the rest of the options set as default in compute environments.

### Job Queue

Now, attach the compute environment to the job queue.

1. Click "create queue" in "Job Queues"
2. Give a queue name
3. Give a priority (e.g., `1`)
4. Attach the compute environment you just created to the job queue
5. Click "Create Job Queue"

![queue](https://i.imgur.com/wJk8Og0.png)

TODO

- link to batch documentation
- IAM role
- compute environment
- other thing 1
- other thing 2
  - define particular ec2 instances
  - memory
  - vCPU's
  - key-pair

## Running the Pipeline

## Monitoring Runs

TODO

- CloudWatch
- EC2 console
- SSH
