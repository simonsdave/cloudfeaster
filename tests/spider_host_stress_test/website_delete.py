#!/usr/bin/env python

import os
import sys

import boto
from boto.s3.connection import S3Connection
 
def delete_website(bucket_name):

    conn = S3Connection()
    try:
        website_bucket = conn.get_bucket(bucket_name)
        for key in website_bucket.get_all_keys():
            key.delete()
        website_bucket.delete()
    except:
        pass

if __name__ == "__main__":

    if 2 != len(sys.argv):
        filename = os.path.split(sys.argv[0])[1]
        sys.exit('usage: %s <bucket-name>' % filename)

    delete_website(sys.argv[1])
