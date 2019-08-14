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

## Initial Setup : Batch Console

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
