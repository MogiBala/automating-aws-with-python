#!/usr/bin/python
# -*- coding: utf -*-

"""configuring AWS S3 buckets
   -Create buckets
   -list list_buckets
   -Sync Local directory to s3"""



import boto3
import click
from botocore.exceptions import ClientError
from pathlib import Path
import mimetypes

session = boto3.Session(profile_name = 'ec2automate')

s3 = session.resource('s3')


@click.group()
def cli():
    "webtron deploys website to AWS"
    pass
@cli.command('list-buckets')
def list_buckets():
   "List all s3 buckets"
   for bucket in s3.buckets.all():
    print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List bucket objects"
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
     "Create and configure an s3 bucket"

     try:
        s3bucket = s3.create_bucket(Bucket=bucket,
           CreateBucketConfiguration={ 'LocationConstraint': session.region_name})
     except ClientError as error:
        if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3bucket = s3.Bucket(bucket)
        else:
            raise error


     policy = """{"Version":"2012-10-17",
          "Statement":    [{     "Sid":"PublicReadGetObject",
              "Effect":"Allow", "Principal": "*",
               "Action":["s3:GetObject"],
               "Resource":["arn:aws:s3:::%s/*"]
               }]}""" % s3bucket.name

     pol = s3bucket.Policy()

     pol.put(Policy=policy)






     ws = s3bucket.Website()

     ws.put(WebsiteConfiguration =
     {
        'ErrorDocument': {
            'Key': 'error.html'
            },
        'IndexDocument': {
            'Suffix': 'index.html'
            }
     })

def upload_file(s3bucket, path, key):
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    s3bucket.upload_file(
         path,
         key,
         ExtraArgs={'ContentType': content_type}
    )
@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    "sync contents of PATHNAME to Bucket"
    s3bucket = s3.Bucket(bucket)

    root = Path(pathname).expanduser().resolve()

    def handle_directory(target):
        for p in target.iterdir():
          if p.is_dir():
              handle_directory(p)
          if p.is_file():
              upload_file(s3bucket, str(p), str(p.relative_to(root)))

    handle_directory(root)


if __name__ == '__main__':
    cli()
