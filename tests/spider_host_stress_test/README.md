Spider Host Stress Testing
==========================

Spider Hosts are intended to run on a machine running in an
IaaS cloud infrastructure (EC2 being the obvious choice).
Some key questions that must be answered:
* how many browsers can a single Xvfb support?
* how many browsers can be simultanously running and
what's the constraining resource (ie do we need more
CPU, RAM, network I/O, disk I/O, etc to be able to run
more browsers)?
* related to the above, if the IaaS offers a variety of
machine types with increasing resource (CPU, RAM, etc) 
being available at increasing cost, what's the right
machine type to use that optimizes cost? 
