# Development Environment

To increase predicability, it is recommended
that Cloudfeaster development be done on a [Vagrant](http://www.vagrantup.com/) provisioned
[VirtualBox](https://www.virtualbox.org/)
VM running [Ubuntu 14.04](http://releases.ubuntu.com/14.04/).
Below are the instructions for spinning up such a VM.

Spin up a VM using [create_dev_env.sh](create_dev_env.sh)
(instead of using ```vagrant up```).

```bash
>./create_dev_env.sh
github username> simonsdave
github email> simonsdave@gmail.com
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'trusty'...
.
.
.
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

Clone the [Cloudfeaster](https://github.com/simonsdave/cloudfeaster) repo.

```bash
vagrant@vagrant-ubuntu-trusty-64:~$ git clone https://github.com/simonsdave/cloudfeaster.git
Cloning into 'cloudfeaster'...
remote: Counting objects: 2377, done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 2377 (delta 0), reused 0 (delta 0), pack-reused 2374
Receiving objects: 100% (2377/2377), 344.78 KiB | 0 bytes/s, done.
Resolving deltas: 100% (1526/1526), done.
Checking connectivity... done.
vagrant@vagrant-ubuntu-trusty-64:~$
```

Install all pre-reqs.

```bash
vagrant@vagrant-ubuntu-trusty-64:~$ cd cloudfeaster
vagrant@vagrant-ubuntu-trusty-64:~/cloudfeaster$ source cfg4dev
New python executable in env/bin/python
Installing setuptools, pip...done.
.
.
.
```

Run all unit & integration tests.

```bash
(env)vagrant@vagrant-ubuntu-trusty-64:~/cloudfeaster$ coverage erase
(env)vagrant@vagrant-ubuntu-trusty-64:~/cloudfeaster$ nosetests --with-coverage
.............................................................
Name                               Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------------------
cloudfeaster/spider.py               204      4     54      3    97%   317-319, 326, 271->264, 315->317, 325->326
cloudfeaster/util/tsh.py              10      0      0      0   100%
cloudfeaster/webdriver_spider.py     107      0     34      0   100%
------------------------------------------------------------------------------
TOTAL                                321      4     88      3    98%
----------------------------------------------------------------------
Ran 61 tests in 82.111s

OK
(env)vagrant@vagrant-ubuntu-trusty-64:~/cloudfeaster$
```
