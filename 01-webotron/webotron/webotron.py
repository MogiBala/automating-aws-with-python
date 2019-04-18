import boto3
import click
from botocore.exceptions import ClientError

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
     except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3bucket = s3.Bucket(bucket)
        else:
            raise e


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

if __name__ == '__main__':
    cli()