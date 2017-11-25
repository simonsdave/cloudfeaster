# Contributing
The following instructions describe how to setup a your development
environment on Mac OS X.

## Getting Started
See [this](../dev_env) for details of how to configure a development environment
and get the automated tests working.

## User Agent Headers

How do I find out the user agent header?
Try [this](http://www.whoishostingthis.com/tools/user-agent/) web site.

## Google Chrome Version

How do I figure out what version of Chrome I'm using?
On Ubuntu try ```google-chrome --version```.

## Coverage Report

How can I generate a coverage report?
From Cloudfeaster's root directory run the following:
~~~~~
coverage erase
rm -rf ./coverage_report/
nosetests --with-coverage
coverage html
~~~~~
An HTML version of the coverage report can now be found in coverage_report/index.html
