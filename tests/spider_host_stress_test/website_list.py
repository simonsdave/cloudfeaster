#!/usr/bin/env python

import os
import sys
import uuid

import boto
from boto.s3.connection import S3Connection
 
def list_websites():

    conn = S3Connection()
    for bucket in conn.get_all_buckets():
        try:
            bucket.get_website_configuration()
            print bucket
        except:
            pass

if __name__ == "__main__":

    if 1 != len(sys.argv):
        filename = os.path.split(sys.argv[0])[1]
        sys.exit('usage: %s' % filename)

    list_websites()
