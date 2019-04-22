#!/usr/bin/python
# -*- coding: utf -*-

"""configuring AWS S3 buckets
   -Create buckets
   -list list_buckets
   -Sync Local directory to s3"""


import boto3
import click
from bucket import BucketManager

session = None
bucket_manager = None

@click.group()
@click.option('--profile', default=None,help="Use a given AWS profile.")
def cli(profile):
    "webtron deploys website to AWS"
    global session, bucket_manager

    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile

    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)                 #s3 = session.resource('s3') defined in bucket.py


@cli.command('list-buckets')
def list_buckets():
   "List all s3 buckets"
   for bucket in bucket_manager.all_buckets():
    print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List bucket objects"
    for obj in bucket_manager.all_objects(bucket):
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
     "Create and configure an s3 bucket"
     s3_bucket = bucket_manager.init_bucket(bucket)

     bucket_manager.set_policy(s3_bucket)
     bucket_manager.configure_website(s3_bucket)


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    "sync contents of PATHNAME to Bucket"

    bucket_manager.sync(pathname, bucket)
    print(bucket_manager.get_bucket_url(bucket_manager.s3.Bucket(bucket)))


if __name__ == '__main__':
    cli()
