import boto3
import os

import logging

from control.config.ec2_config import EC2Config


class S3Manager:

    def __init__(self, aws_config=None):
        if aws_config is None:
            aws_config = EC2Config()

        self.aws_config = aws_config

        self.client = boto3.client('s3')
        self.resource = boto3.resource('s3')

    @property
    def bucket(self):
        return self.resource.Bucket(self.aws_config.bucket_name)

    def has_object(self, object_str):
        objects = list(self.bucket.objects.filter(Prefix=object_str))

        return len(objects) > 0

    def create_object(self, object_str):
        obj = self.bucket.Object(key=object_str)
        obj.put()
        self.bucket.wait_until_exists(object_str)

        logging.info("Creating object {} on bucket {}".format(object_str,
                                                              self.bucket.name)
                     )

    def delete_object(self, object_str):
        obj = self.bucket.Object(key=object_str)
        obj.delete()
        logging.info("Deleting object {} from bucket {}".format(object_str,
                                                                self.bucket.name)
                     )

    def rename_object(self, object_str):
        pass

    def upload_object(self, source_path, dest_path, object_name):
        with open(source_path + object_name, 'rb') as data:
            self.client.upload_fileobj(data, self.bucket.name, dest_path + object_name)

            self.bucket.wait_until_exists(dest_path + object_name)

        logging.info("Uploading object {} to bucket {} path {}".format(object_name,
                                                                       self.bucket.name,
                                                                       dest_path))

    def upload_all_files(self, source_path, dest_path):

        for root, dirs, files in os.walk(source_path):
            for file in files:
                self.upload_object(source_path=root + "/",
                                   dest_path=dest_path + os.path.relpath(root, source_path) + "/",
                                   object_name=file
                                   )
