Spider Host Stress Test
=======================

Spider Hosts are intended to run on a machine running in an
IaaS offering ([EC2](http://aws.amazon.com/ec2/) being an obvious choice).
Some key questions that must be answered:

* how many browsers can a single
[Xvfb](http://en.wikipedia.org/wiki/Xvfb) support?
* how many browsers can be simultanously running on a single
machine and what's the constraining resource (ie do we need more
CPU, RAM, network I/O, disk I/O, etc to be able to run
more browsers on that single machine)?
* related to the above, if the IaaS offers a variety of
machine types with increasing resource (CPU, RAM, etc) 
being available at increasing cost, what's the right
machine type to use that optimizes cost?

The primary objective of Spider Host Stress Testing is to
generate the raw data required to answer the above questions.
A secondary objective is to use the desire to automate the
stress testing process as a way to drive out any problems
with the CloudFeaster packaging configuration and, perhaps
more importantly, drive out problems with the automated provisioning
across a variety of IaaS offerings.

References
==========

When automating the Spider Host Stress Tests, the following references
where very helpful

* [Sample script for creating a website in an S3 bucket with boto](https://gist.github.com/garnaat/833135)
* [Hosting a Static Website on Amazon S3](http://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html)
* [Create your own git server easily with Chef and the Vagrant AWS plugin: Part 1.](http://minimul.com/create-your-own-git-server-easily-with-chef-and-the-vagrant-aws-plugin-part-1.html)
* [Docker/Amazon EC2/Vagrant](http://docs.docker.io/en/latest/installation/amazon/#amazonvagrant)
* [Use Vagrant to manage your EC2 and VPC instances](https://github.com/mitchellh/vagrant-aws)
* [Ubuntu 12.04.2 LTS (Precise Pangolin) - Amazon EC2 Published AMIs](http://cloud-images.ubuntu.com/releases/precise/release-20130411.1/)
