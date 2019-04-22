# -*- coding -*-


import mimetypes
from pathlib import Path
from botocore.exceptions import ClientError


"""Classes for S3 buckets"""
class BucketManager:
    """MAnage an s3 bucket."""

    def __init__(self, session):
        """creates a BucketManager object."""
        self.session = session
        self.s3 = self.session.resource('s3')

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
    def upload_file(bucket, path, key):
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        return bucket.upload_file(
             path,
             key,
             ExtraArgs={'ContentType': content_type}
        )

    def sync(self, pathname, bucket_name):
        bucket = self.s3.Bucket(bucket_name)

        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
              if p.is_dir():
                  handle_directory(p)
              if p.is_file():
                  self.upload_file(bucket, str(p), str(p.relative_to(root)))

        handle_directory(root)
