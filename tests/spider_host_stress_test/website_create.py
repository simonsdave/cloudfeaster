#!/usr/bin/env python

import os
import sys
import uuid

import boto
from boto.s3.connection import S3Connection
 
def create_key(website_bucket, key_name, html):
    key = website_bucket.new_key(key_name)
    key.content_type = 'text/html'
    key.set_contents_from_string(html, policy='public-read')
    return key

def create_index_dot_html(website_bucket):
    html = (
        '<html>'
        '<head>'
        '<title>My Website</title>'
        '</head>'
        '<body>'
        '<form name="input" action="myaccount.html" method="get">'
        'Username: <input type="text" name="user">'
        'Password: <input type="text" name="password">'
        '<input type="submit" value="Submit">'
        '</form>'
        '</body>'
        '</html>'
    )
    return create_key(website_bucket, 'index.html', html)
 
def create_error_dot_html(website_bucket):
    html = (
        '<html>'
        '<head><title>That Nasty 404 Thing:-(</title></head>'
        '<body><h1>Oops ...</h1></body>'
        '</html>'
    )
    return create_key(website_bucket, 'error.html', html)
 
def create_myaccount_dot_html(website_bucket):
    html = (
        '<html>'
        '<head>'
        '<script type="text/javascript">'
        'function addBalanceElement() {'
        '    var balance = document.createElement("span");'
        '    balance.innerHTML = "42,000";'
        '    balance.setAttribute("id", "43");'
        '    var element = document.getElementById("balancediv");'
        '    element.appendChild(balance);'
        '}'
        '</script>'
        '<title>My Account</title>'
        '</head>'
        '<body onload="setTimeout(\'addBalanceElement()\',3000)">'
        '<h1>My Account</h1>'
        '<h2>Balance</h2>'
        '<div id="balancediv">'
        '</div>'
        '</body>'
        '</html>'
    )
    return create_key(website_bucket, 'myaccount.html', html)
 
def create_website():
    conn = S3Connection()
    bucket_name = str(uuid.uuid4())
    website_bucket = conn.create_bucket(
        bucket_name,
        location=boto.s3.connection.Location.DEFAULT,
        policy='public-read'
    )
    index_key = create_index_dot_html(website_bucket)
    error_key = create_error_dot_html(website_bucket)
    website_bucket.configure_website(index_key.name, error_key.name)

    create_myaccount_dot_html(website_bucket)

    print "http://%s.s3-website-us-east-1.amazonaws.com/" % bucket_name

if __name__ == "__main__":

    if 1 != len(sys.argv):
        filename = os.path.split(sys.argv[0])[1]
        sys.exit('usage: %s' % filename)

    create_website()
