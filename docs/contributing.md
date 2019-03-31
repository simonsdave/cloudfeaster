# Contributing

The following instructions describe how you can contribute
to this project.

## Getting Started

See [this](../dev_env) for details of how to configure a development environment
and get the automated tests working.

## Branching and Versioning Strategy

* all development is done on the ```master``` branch
* we use [Semantic Versioning](http://semver.org/)
* for each release a new branch is created from master called ```release-<version>```

## How To Cut a Release

* this process leverages all the good work in the [simonsdave / dev-env](https://github.com/simonsdave/dev-env) project
* the shell script ```prep-for-release-python.sh``` automates much of the release process
* make sure your ```~/.pypirc``` is setup

```bash
(env)>prep-for-release-python.sh
Already on 'master'
Your branch is up to date with 'origin/master'.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 0a70027..a420aa6 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -3,7 +3,7 @@ All notable changes to this project will be documented in this file.
 Format of this file follows [these](http://keepachangelog.com/) guidelines.
 This project adheres to [Semantic Versioning](http://semver.org/).

-## [%RELEASE_VERSION%] - [%RELEASE_DATE%]
+## [0.9.15] - [2019-03-30]

 ### Added

These changes to master for release look ok? (y/n)> y
```

```bash
[master 675b771] 0.9.15 pre-release prep
 1 file changed, 1 insertion(+), 1 deletion(-)
diff --git a/CHANGELOG.md b/CHANGELOG.md
index a420aa6..37733b7 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -3,6 +3,20 @@ All notable changes to this project will be documented in this file.
 Format of this file follows [these](http://keepachangelog.com/) guidelines.
 This project adheres to [Semantic Versioning](http://semver.org/).

+## [%RELEASE_VERSION%] - [%RELEASE_DATE%]
+
+### Added
+
+* Nothing
+
+### Changed
+
+* Nothing
+
+### Removed
+
+* Nothing
+
 ## [0.9.15] - [2019-03-30]

 ### Added
diff --git a/cloudfeaster/__init__.py b/cloudfeaster/__init__.py
index 2e2937e..2affa6a 100644
--- a/cloudfeaster/__init__.py
+++ b/cloudfeaster/__init__.py
@@ -1 +1 @@
-__version__ = '0.9.15'
+__version__ = '0.9.16'
These changes to master for next release look ok? (y/n)> y
```

```bash
[master 3dcdca8] Prep CHANGELOG.md for next release
 2 files changed, 15 insertions(+), 1 deletion(-)
Switched to branch 'release-0.9.15'
e407879a4b64424cbc953c677c16c6e8
running bdist_wheel
running build
running build_py
creating build
creating build/lib.linux-x86_64-2.7
creating build/lib.linux-x86_64-2.7/cloudfeaster
copying cloudfeaster/__init__.py -> build/lib.linux-x86_64-2.7/cloudfeaster
copying cloudfeaster/spider.py -> build/lib.linux-x86_64-2.7/cloudfeaster
copying cloudfeaster/jsonschemas.py -> build/lib.linux-x86_64-2.7/cloudfeaster
creating build/lib.linux-x86_64-2.7/cloudfeaster/samples
copying cloudfeaster/samples/pypi.py -> build/lib.linux-x86_64-2.7/cloudfeaster/samples
copying cloudfeaster/samples/pythonwheels.py -> build/lib.linux-x86_64-2.7/cloudfeaster/samples
copying cloudfeaster/samples/__init__.py -> build/lib.linux-x86_64-2.7/cloudfeaster/samples
copying cloudfeaster/samples/xe_exchange_rates.py -> build/lib.linux-x86_64-2.7/cloudfeaster/samples
running egg_info
creating cloudfeaster.egg-info
writing requirements to cloudfeaster.egg-info/requires.txt
writing cloudfeaster.egg-info/PKG-INFO
writing top-level names to cloudfeaster.egg-info/top_level.txt
writing dependency_links to cloudfeaster.egg-info/dependency_links.txt
writing manifest file 'cloudfeaster.egg-info/SOURCES.txt'
reading manifest file 'cloudfeaster.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
writing manifest file 'cloudfeaster.egg-info/SOURCES.txt'
creating build/lib.linux-x86_64-2.7/cloudfeaster/jsonschemas
copying cloudfeaster/jsonschemas/spider_metadata.json -> build/lib.linux-x86_64-2.7/cloudfeaster/jsonschemas
copying cloudfeaster/jsonschemas/spider_output.json -> build/lib.linux-x86_64-2.7/cloudfeaster/jsonschemas
installing to build/bdist.linux-x86_64/wheel
running install
running install_lib
creating build/bdist.linux-x86_64
creating build/bdist.linux-x86_64/wheel
creating build/bdist.linux-x86_64/wheel/cloudfeaster
copying build/lib.linux-x86_64-2.7/cloudfeaster/__init__.py -> build/bdist.linux-x86_64/wheel/cloudfeaster
creating build/bdist.linux-x86_64/wheel/cloudfeaster/samples
copying build/lib.linux-x86_64-2.7/cloudfeaster/samples/pypi.py -> build/bdist.linux-x86_64/wheel/cloudfeaster/samples
copying build/lib.linux-x86_64-2.7/cloudfeaster/samples/pythonwheels.py -> build/bdist.linux-x86_64/wheel/cloudfeaster/samples
copying build/lib.linux-x86_64-2.7/cloudfeaster/samples/__init__.py -> build/bdist.linux-x86_64/wheel/cloudfeaster/samples
copying build/lib.linux-x86_64-2.7/cloudfeaster/samples/xe_exchange_rates.py -> build/bdist.linux-x86_64/wheel/cloudfeaster/samples
copying build/lib.linux-x86_64-2.7/cloudfeaster/spider.py -> build/bdist.linux-x86_64/wheel/cloudfeaster
creating build/bdist.linux-x86_64/wheel/cloudfeaster/jsonschemas
copying build/lib.linux-x86_64-2.7/cloudfeaster/jsonschemas/spider_output.json -> build/bdist.linux-x86_64/wheel/cloudfeaster/jsonschemas
copying build/lib.linux-x86_64-2.7/cloudfeaster/jsonschemas/spider_metadata.json -> build/bdist.linux-x86_64/wheel/cloudfeaster/jsonschemas
copying build/lib.linux-x86_64-2.7/cloudfeaster/jsonschemas.py -> build/bdist.linux-x86_64/wheel/cloudfeaster
running install_egg_info
Copying cloudfeaster.egg-info to build/bdist.linux-x86_64/wheel/cloudfeaster-0.9.15.egg-info
running install_scripts
creating build/bdist.linux-x86_64/wheel/cloudfeaster-0.9.15.dist-info/WHEEL
running sdist
running check
creating cloudfeaster-0.9.15
creating cloudfeaster-0.9.15/cloudfeaster
creating cloudfeaster-0.9.15/cloudfeaster.egg-info
creating cloudfeaster-0.9.15/cloudfeaster/jsonschemas
creating cloudfeaster-0.9.15/cloudfeaster/samples
making hard links in cloudfeaster-0.9.15...
hard linking MANIFEST.in -> cloudfeaster-0.9.15
hard linking README.rst -> cloudfeaster-0.9.15
hard linking setup.cfg -> cloudfeaster-0.9.15
hard linking setup.py -> cloudfeaster-0.9.15
hard linking cloudfeaster/__init__.py -> cloudfeaster-0.9.15/cloudfeaster
hard linking cloudfeaster/jsonschemas.py -> cloudfeaster-0.9.15/cloudfeaster
hard linking cloudfeaster/spider.py -> cloudfeaster-0.9.15/cloudfeaster
hard linking cloudfeaster.egg-info/PKG-INFO -> cloudfeaster-0.9.15/cloudfeaster.egg-info
hard linking cloudfeaster.egg-info/SOURCES.txt -> cloudfeaster-0.9.15/cloudfeaster.egg-info
hard linking cloudfeaster.egg-info/dependency_links.txt -> cloudfeaster-0.9.15/cloudfeaster.egg-info
hard linking cloudfeaster.egg-info/requires.txt -> cloudfeaster-0.9.15/cloudfeaster.egg-info
hard linking cloudfeaster.egg-info/top_level.txt -> cloudfeaster-0.9.15/cloudfeaster.egg-info
hard linking cloudfeaster/jsonschemas/spider_metadata.json -> cloudfeaster-0.9.15/cloudfeaster/jsonschemas
hard linking cloudfeaster/jsonschemas/spider_output.json -> cloudfeaster-0.9.15/cloudfeaster/jsonschemas
hard linking cloudfeaster/samples/__init__.py -> cloudfeaster-0.9.15/cloudfeaster/samples
hard linking cloudfeaster/samples/pypi.py -> cloudfeaster-0.9.15/cloudfeaster/samples
hard linking cloudfeaster/samples/pythonwheels.py -> cloudfeaster-0.9.15/cloudfeaster/samples
hard linking cloudfeaster/samples/xe_exchange_rates.py -> cloudfeaster-0.9.15/cloudfeaster/samples
copying setup.cfg -> cloudfeaster-0.9.15
Writing cloudfeaster-0.9.15/setup.cfg
Creating tar archive
removing 'cloudfeaster-0.9.15' (and everything under it)
c1eec9a444194b7a86f336f6b818404c
diff --git a/README.md b/README.md
index e1d7be5..ee2e85d 100644
--- a/README.md
+++ b/README.md
@@ -5,7 +5,7 @@
 ![status](https://img.shields.io/pypi/status/cloudfeaster.svg?style=flat)
 [![PyPI](https://img.shields.io/pypi/v/cloudfeaster.svg?style=flat)](https://pypi.python.org/pypi/cloudfeaster)
 [![Requirements](https://requires.io/github/simonsdave/cloudfeaster/requirements.svg?branch=master)](https://requires.io/github/simonsdave/cloudfeaster/requirements/?branch=master)
-[![CircleCI](https://circleci.com/gh/simonsdave/cloudfeaster/tree/master.svg?style=svg)](https://circleci.com/gh/simonsdave/cloudfeaster/tree/master)
+[![CircleCI](https://circleci.com/gh/simonsdave/cloudfeaster/tree/release-0.9.15.svg?style=svg)](https://circleci.com/gh/simonsdave/cloudfeaster/tree/release-0.9.15)
 [![Coverage Status](https://coveralls.io/repos/simonsdave/cloudfeaster/badge.svg?style=flat)](https://coveralls.io/r/simonsdave/cloudfeaster)
 [![docker-simonsdave/cloudfeaster-xenial-dev-env](https://img.shields.io/badge/dockerhub-simonsdave%2Fcloudfeaster--xenial--dev-blue.svg)](https://hub.docker.com/r/simonsdave/cloudfeaster-xenial-dev-env)

@@ -15,14 +15,14 @@ modern software engineering tools, services and trends to create:
 * (this repo is) [a spider authoring and maintenance environment](https://github.com/simonsdave/cloudfeaster)
 * a service infrastructure for discovering and running spiders via a RESTful API

-[This](docs/story.md) is the story behind Cloudfeaster.
+[This](https://github.com/simonsdave/cloudfeaster/tree/release-0.9.15/docs/story.md) is the story behind Cloudfeaster.

 ## What Next

-* see [these](docs/contributing.md) instructions
+* see [these](https://github.com/simonsdave/cloudfeaster/tree/release-0.9.15/docs/contributing.md) instructions
 describe how to setup your development environment and
 start contributing to Cloudfeaster
-* [this](docs/spider_authors.md) describes
+* [this](https://github.com/simonsdave/cloudfeaster/tree/release-0.9.15/docs/spider_authors.md) describes
 how to author spiders using Cloudfeaster
 * take a look at these sample spiders
   * [cloudfeaster/samples](cloudfeaster/samples/)
These changes to release-0.9.15 look ok? (y/n)> y
```

```bash
[release-0.9.15 b01f49a] 0.9.15 release prep
 1 file changed, 4 insertions(+), 4 deletions(-)
All changes made locally. Ok to push changes to github? (y/n)> y
Switched to branch 'master'
Your branch is ahead of 'origin/master' by 2 commits.
  (use "git push" to publish your local commits)
Enter passphrase for key '/Users/dave/.ssh/id_rsa':
Counting objects: 8, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (7/7), done.
Writing objects: 100% (8/8), 762 bytes | 762.00 KiB/s, done.
Total 8 (delta 5), reused 0 (delta 0)
remote: Resolving deltas: 100% (5/5), completed with 3 local objects.
To github.com:simonsdave/cloudfeaster.git
   f49e304..3dcdca8  master -> master
Switched to branch 'release-0.9.15'
Enter passphrase for key '/Users/dave/.ssh/id_rsa':
Counting objects: 3, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 356 bytes | 356.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0)
remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
remote:
remote: Create a pull request for 'release-0.9.15' on GitHub by visiting:
remote:      https://github.com/simonsdave/cloudfeaster/pull/new/release-0.9.15
remote:
To github.com:simonsdave/cloudfeaster.git
 * [new branch]      release-0.9.15 -> release-0.9.15
Switched to branch 'master'
Your branch is up to date with 'origin/master'.
(env)>
```

```bash
(env)>upload-dist-to-pypi.sh testpypi
Uploading distributions to https://test.pypi.org/legacy/
Uploading cloudfeaster-0.9.15-py2-none-any.whl
100%|##########| 24.7k/24.7k [00:03<00:00, 7.12kB/s]
Uploading cloudfeaster-0.9.15.tar.gz
100%|##########| 20.3k/20.3k [00:01<00:00, 12.4kB/s]
(env)>
```

Now look on [https://test.pypi.org/project/cloudfeaster/](https://test.pypi.org/project/cloudfeaster/)
to confirm all is ok and if it is upload to the test version of pypi.

```bash
(env) ~/cloudfeaster> twine upload dist/*
Uploading distributions to https://upload.pypi.org/legacy/
Uploading cloudfeaster-0.9.8-py2-none-any.whl
Uploading cloudfeaster-0.9.8.tar.gz
(env) ~/cloudfeaster>
```

Now look on [https://pypi.org/project/cloudfeaster/](https://pypi.org/project/cloudfeaster/)
to confirm all is ok and if it is upload to the production version of pypi.

```bash
(env) ~/cloudfeaster> cd dist/
(env) ~/cloudfeaster/dist> cp * /vagrant/.
(env) ~/cloudfeaster/dist> ls -la /vagrant/cloudfeaster*
-rw-r--r-- 1 vagrant vagrant 18987 Jan 10 14:19 /vagrant/cloudfeaster-0.9.8-py2-none-any.whl
-rw-r--r-- 1 vagrant vagrant 15642 Jan 10 14:19 /vagrant/cloudfeaster-0.9.8.tar.gz
(env) ~/cloudfeaster>
```

* on the [releases](https://github.com/simonsdave/cloudfeaster/releases)
page hit the <Draft a new release> button in the upper right corner
* fill out the release form as per the screenshot below
* main body of the form can be pulled directly from [CHANGELOG.md](../CHANGELOG.md)
* don't forget to attach to the release the ```cloudfeaster-*.whl``` and ```cloudfeaster-*.tar.gz```
copied to ```/vagrant``` in one of the above steps

![](images/release-form.png)
