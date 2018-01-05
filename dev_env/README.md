# Development Environment

To increase predicability, it is recommended
that Cloudfeaster development be done on a [Vagrant](http://www.vagrantup.com/) provisioned
[VirtualBox](https://www.virtualbox.org/)
VM running [Ubuntu 14.04](http://releases.ubuntu.com/14.04/).
Below are the instructions for spinning up such a VM.

Spin up a VM using [create_dev_env.sh](create_dev_env.sh)
(instead of using ```vagrant up```).

```bash
>./create_dev_env.sh simonsdave simonsdave@gmail.com ~/.ssh/id_rsa.pub ~/.ssh/id_rsa
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'trusty'...
.
.
.
>
```

SSH into the VM.

```bash
>vagrant ssh
Welcome to Ubuntu 14.04 LTS (GNU/Linux 3.13.0-27-generic x86_64)

 * Documentation:  https://help.ubuntu.com/

 System information disabled due to load higher than 1.0

  Get cloud support with Ubuntu Advantage Cloud Guest:
    http://www.ubuntu.com/business/services/cloud

0 packages can be updated.
0 updates are security updates.


vagrant@vagrant-ubuntu-trusty-64:~$
```

Start the ssh-agent in the background.

```bash
~> eval "$(ssh-agent -s)"
Agent pid 25657
~>
```

Add SSH private key for github to the ssh-agent

```bash
~> ssh-add ~/.ssh/id_rsa_github
Enter passphrase for /home/vagrant/.ssh/id_rsa_github:
Identity added: /home/vagrant/.ssh/id_rsa_github (/home/vagrant/.ssh/id_rsa_github)
~>
```

Clone the repo.

```bash
~> git clone git@github.com:simonsdave/cloudfeaster.git
Cloning into 'cloudfeaster'...
remote: Counting objects: 3101, done.
remote: Total 3101 (delta 0), reused 0 (delta 0), pack-reused 3101
Receiving objects: 100% (3101/3101), 459.37 KiB | 0 bytes/s, done.
Resolving deltas: 100% (1985/1985), done.
Checking connectivity... done.
~>
```

Install all pre-reqs.

```bash
~> cd cloudfeaster
~/cloudfeaster> source cfg4dev
New python executable in env/bin/python
Installing setuptools, pip...done.
.
.
.
(env)~/cloudfeaster> source cfg4dev
```

Run all unit & integration tests.

```bash
(env) ~/cloudfeaster> nosetests --with-coverage --cover-branches --cover-erase --cover-package cloudfeaster bin/tests cloudfeaster
Coverage.py warning: --include is ignored because --source is set (include-ignored)
.................................................SS.................
Name                               Stmts   Miss Branch BrPart  Cover
--------------------------------------------------------------------
cloudfeaster/spider.py               239     14     54      4    94%
cloudfeaster/webdriver_spider.py     131      4     42      2    97%
--------------------------------------------------------------------
TOTAL                                370     18     96      6    95%
----------------------------------------------------------------------
Ran 68 tests in 78.069s

OK (SKIP=2)
(env)~/cloudfeaster>
```
