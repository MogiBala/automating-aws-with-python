# -*- coding -*-


import mimetypes
from pathlib import Path
import boto3
from functools import reduce
from botocore.exceptions import ClientError
from hashlib import md5
from webotron import utils


"""Classes for S3 buckets"""
class BucketManager:
    """MAnage an s3 bucket."""

    CHUNK_SIZE = 8388608                          #in bites value taken from Boto3 docs s3 customization references https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#s3-transfers

    def __init__(self, session):
        """creates a BucketManager object."""
        self.session = session
        self.s3 = self.session.resource('s3')
        self.transfer_config = boto3.s3.transfer.TransferConfig(               #refer s3 customization references
              multipart_chunksize=self.CHUNK_SIZE,
              multipart_threshold=self.CHUNK_SIZE
        )

        self.manifest = {}

    def load_manifest(self, bucket):
        """ load manifest for caching purpose"""
        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket.name):
            for obj in page.get('Contents', []):
                self.manifest[obj['Key']] = obj['ETag']                         #obje[key] are key names of s3 files and obj[Etag] is etag of that file
                                                                                # so structure of manifest dictionary is ex: {index.html: "Etag"}
    def get_bucket(self, bucket_name):
        """Get a bucket object by name"""
        return self.s3.Bucket(bucket_name)                          #return bucket object by taking domain name to create a bucket with domain name -  webotron.py/setup_domain()

    def get_region_name(self, bucket):
        """get the bucket region name"""
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket=bucket.name)  #gets the location of bucket where it is created

        return bucket_location["LocationConstraint"] or 'us-east-1'          # in AWS API the LocationConstraint for U east 1 is None

    def get_bucket_url(self, bucket):
        """get url of the bucket created"""
        return "hhtp://{}.{}".format(bucket.name, utils.get_endpoint(self.get_region_name(bucket)).host)

    def all_buckets(self):
        """Get an iterator for all buckets"""
        return self.s3.buckets.all()


    def all_objects(self, bucket_name):
      """Get an iterator for all bucket objects"""
      return self.s3.Bucket(bucket_name).objects.all()


    def init_bucket(self, bucket_name):
        "create bucket or initialize existing bucket"
        try:
           s3bucket = self.s3.create_bucket(Bucket=bucket_name,
              CreateBucketConfiguration={ 'LocationConstraint': self.session.region_name})
        except ClientError as error:
           if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
               s3bucket = self.s3.Bucket(bucket_name)
           else:
               raise error

        return s3bucket

    def set_policy(self, bucket):
             """set bucket policy"""

             policy = """{"Version":"2012-10-17",
                  "Statement":    [{     "Sid":"PublicReadGetObject",
                      "Effect":"Allow", "Principal": "*",
                       "Action":["s3:GetObject"],
                       "Resource":["arn:aws:s3:::%s/*"]
                       }]}""" % bucket.name

             pol = bucket.Policy()

             pol.put(Policy=policy)



    def configure_website(self, bucket):
         """ configuring website"""

         bucket.Website().put(WebsiteConfiguration =
          {
             'ErrorDocument': {
                 'Key': 'error.html'
                 },
             'IndexDocument': {
                 'Suffix': 'index.html'
                 }
          })

    @staticmethod
    def hash_data(data):
        """ to generate md5 hash"""
        hash = md5()
        hash.update(data)

        return hash

    def gen_etag(self, path):
        """Generate etag for file."""
        hashes = []

        with open(path, 'rb') as f:
            while True:
                data = f.read(self.CHUNK_SIZE)

                if not data:
                    break

                hashes.append(self.hash_data(data))
        if not hashes:                         #in case theres no data
            return

        elif len(hashes) == 1:                      #incase there is only one hash tag or Etag
            return '"{}"'.format(hashes[0].hexdigest())

        else:
            hash = self.hash_data(reduce(lambda x,y: x+y, (h.digest() for h in hashes)))   #takes all the hash and inturn creates a has for the summation
            return '"{}-{}"'.format(hash.hexdigest(), len(hashes))


    def upload_file(self, bucket, path, key):
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        etag = self.gen_etag(path)
        if self.manifest.get(key, '') == etag:
            print("Skipping {}, etags match".format(key))
            return
        return bucket.upload_file(
             path,
             key,
             ExtraArgs={'ContentType': content_type},
             Config=self.transfer_config
        )

    def sync(self, pathname, bucket_name):
        bucket = self.s3.Bucket(bucket_name)
        self.load_manifest(bucket)

        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
              if p.is_dir():
                  handle_directory(p)
              if p.is_file():
                  self.upload_file(bucket, str(p), str(p.relative_to(root)))     #upload function is called and the etag is checked for everyfile in upload_file

        handle_directory(root)
