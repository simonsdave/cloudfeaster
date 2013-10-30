Spider Host Stress Test
=======================

Spider Hosts are intended to run on a machine running in an
IaaS cloud infrastructure ([EC2](http://aws.amazon.com/ec2/)
being an obvious choice).
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
with the CloudFeaster packaging configuration.
