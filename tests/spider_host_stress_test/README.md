Spider Host Stress Test
=======================

Spider Hosts are intended to run on a machine running in an
IaaS offering ([EC2](http://aws.amazon.com/ec2/) being an obvious choice).
Some key questions that must be answered:

* If the IaaS offers a variety of
machine types with increasing resources (CPU, RAM, etc) 
being available at increasing cost, what's the right
machine type to use that optimizes cost? The metric that will
be used to compare across machine types is "cost per 10 second crawl".
This metric is calculated by dividing the cost per hour of a
machine type and dividing it by the number of 10 second crawls
that can be executed on a machine in an hour.
* How many browsers can a single
[Xvfb](http://en.wikipedia.org/wiki/Xvfb) support?
* How many spiders can be simultanously running on a single
machine and what's the constraining resource (ie do we need more
CPU, RAM, network I/O, disk I/O, etc to be able to run
more browsers on that single machine)?

The primary objective of Spider Host Stress Testing is to
generate the raw data required to answer the above questions.
A secondary objective is to use the desire to automate the
stress testing process as a way to drive out any problems
with the CloudFeaster packaging configuration and, perhaps
more importantly, drive out problems with the automated provisioning
across a variety of IaaS offerings.

Process
=======

The bullet points below outline how the stress test is
performed. In addition, the bullets try to impart some of
the philosophy and "whys" used when creating the infrastructure.

* Figuring out how many spiders can simultaneously run on
a single machine is essential to optimizing operational costs.
* It was believed that we'd frequently want/need
to run stress tests and therefore a heavy emphasis was placed
on automating the stress testing process.
* A single Python script controls overall execution of the test.
* Web sites to crawl during the stress test are hosted on S3.
Python scripts use [boto](https://github.com/boto/boto)
to create and destroy the sites.
* Spiders to crawl the test web sites are uploaded to the S3
hosted spider repo using the 'clf sr' command.
* 'clf creq c' and 'clf cresq c' commands are used
create spider request and spider response queues in AWS's SQS.
The same scripts overfill the request queue so that during the
stress test all Spider Hosts are constantly busy.
* Vagrant is used to create and provision an AWS EC2 instance
on which Spider Hosts execute.
* Stress tests run for an hour.
* During the first 5 minutes, a single Spider Host chews thru
a bunch of requests. The output of this phase of the test
is used to evaluate the performance of Spiders running under
more stressful conditions in subsequent phases of the test.

Open Questions/Concerns
=======================

Below are a list of open questions and/or concerns that
have yet to be answered and/or addressed.

* How do we know the web sites being crawled in the stress
test are representative of real web sites? This feels like
an important question for AJAX heavy sites that will cause
the browsers to consume lots of resources?
* What mechanism is used to spin up Spider Hosts? 

Notes (Should Not Go Here)
==========================
* vagrant plugin install vagrant-aws
* vagrant plugin list
* vagrant box add awsec2 https://github.com/mitchellh/vagrant-aws/raw/master/dummy.box
* vagrant box list

References
==========

When automating the Spider Host Stress Tests, the following references
where very helpful

* [Sample script for creating a website in an S3 bucket with boto](https://gist.github.com/garnaat/833135)
* [AWS General Reference (Version 1.0) - Regions and Endpoints](http://docs.aws.amazon.com/general/latest/gr/rande.html)
* [Hosting a Static Website on Amazon S3](http://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html)
* [Docker/Amazon EC2/Vagrant](http://docs.docker.io/en/latest/installation/amazon/#amazonvagrant)
* [Use Vagrant to manage your EC2 and VPC instances](https://github.com/mitchellh/vagrant-aws)
* [Ubuntu 12.04.2 LTS (Precise Pangolin) - Amazon EC2 Published AMIs](http://cloud-images.ubuntu.com/releases/precise/release-20130411.1/)
