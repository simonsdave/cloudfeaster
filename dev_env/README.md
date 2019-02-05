# Development Environment

To increase predicability, it is recommended
that Cloudfeaster development be done on a [Vagrant](http://www.vagrantup.com/) provisioned
[VirtualBox](https://www.virtualbox.org/)
VM running [Ubuntu 16.04](http://releases.ubuntu.com/16.04/).
Below are the instructions for spinning up such a VM.

Spin up a VM using [create_dev_env.sh](create_dev_env.sh)
(instead of using ```vagrant up```).

```bash
>./create_dev_env.sh simonsdave simonsdave@gmail.com ~/.ssh/id_rsa.pub ~/.ssh/id_rsa
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'ubuntu/xenial64'...
.
.
.
default: /home/vagrant
>
```

SSH into the VM.

```bash
>vagrant ssh
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-119-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  Get cloud support with Ubuntu Advantage Cloud Guest:
    http://www.ubuntu.com/business/services/cloud

7 packages can be updated.
7 updates are security updates.


~>
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
remote: Counting objects: 3845, done.
remote: Compressing objects: 100% (128/128), done.
remote: Total 3845 (delta 101), reused 109 (delta 51), pack-reused 3664
Receiving objects: 100% (3845/3845), 733.46 KiB | 656.00 KiB/s, done.
Resolving deltas: 100% (2464/2464), done.
Checking connectivity... done.
~>
```

Install all pre-reqs.

```bash
~> cd cloudfeaster
```

```bash
~/cloudfeaster> source cfg4dev
New python executable in /home/vagrant/cloudfeaster/env/bin/python
Installing setuptools, pip, wheel...done.
.
.
.
(env) ~/cloudfeaster>
```

Run all unit & integration tests.

```bash
(env) ~/cloudfeaster> run_unit_tests.sh
Coverage.py warning: --include is ignored because --source is set (include-ignored)
.............................................................SS.................
Name                               Stmts   Miss Branch BrPart  Cover
--------------------------------------------------------------------
cloudfeaster/__init__.py               1      1      0      0     0%
cloudfeaster/jsonschemas.py            8      0      0      0   100%
cloudfeaster/samples/__init__.py       0      0      0      0   100%
cloudfeaster/spider.py               243     14     56      4    94%
cloudfeaster/webdriver_spider.py     131      4     42      2    97%
--------------------------------------------------------------------
TOTAL                                383     19     98      6    95%
----------------------------------------------------------------------
Ran 80 tests in 90.028s

OK (SKIP=2)
(env) ~/cloudfeaster>
```

Build distribution.

```bash
(env) ~/cloudfeaster> build_python_package.sh
running bdist_wheel
running build
running build_py
.
.
.
Creating tar archive
removing 'cloudfeaster-0.9.15' (and everything under it)
3bfb7be2aa16480faa0f82a9a8e8e5eb
(env) ~/cloudfeaster>
```

Build docker image.

```bash
(env) ~/cloudfeaster> ./dockerfiles/build-docker-image.sh dist/cloudfeaster-*.*.*.tar.gz simonsdave/cloudfeaster:latest
Sending build context to Docker daemon   21.5kB
Step 1/18 : FROM ubuntu:16.04
16.04: Pulling from library/ubuntu
.
.
.
 ---> 149a2035a2f8
Successfully built 149a2035a2f8
Successfully tagged simonsdave/cloudfeaster:latest
(env) ~/cloudfeaster>
```

Run docker integration tests.

```bash
(env) ~/cloudfeaster> ./tests/integration/docker_image_integration_tests.sh simonsdave/cloudfeaster:latest $PYPI_USERNAME $PYPI_PASSWORD
.......
Successfully completed 7 integration tests.
(env) ~/cloudfeaster>
```
