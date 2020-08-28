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

* this process leverages lots of the good work in the [simonsdave / dev-env](https://github.com/simonsdave/dev-env) project
* the shell script ```cut-release.sh``` automates much of the release process
* make sure 1/ ```~/.pypirc``` is setup 2/ ```git config --global github.token``` returns
  a [github personal access token](https://github.com/settings/tokens) with
  [scope](https://docs.github.com/en/developers/apps/scopes-for-oauth-apps)
  required to create a release using the [github api](https://developer.github.com/)

```bash
(env) ~> cut-release.sh
Already on 'master'
Your branch is up to date with 'origin/master'.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f77d64c..808826d 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -3,7 +3,7 @@ All notable changes to this project will be documented in this file.
 Format of this file follows [these](http://keepachangelog.com/) guidelines.
 This project adheres to [Semantic Versioning](http://semver.org/).

-## [%RELEASE_VERSION%] - [%RELEASE_DATE%]
+## [0.9.18] - [2019-05-18]

 ### Added

These changes to master for release look ok? (y/n)>
```

```bash
[master a6e04ec] 0.9.18 pre-release prep
 1 file changed, 1 insertion(+), 1 deletion(-)
DEPRECATION: Python 2.7 will reach the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 won't be maintained after that date. A future version of pip will drop support for Python 2.7.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 808826d..e4240d3 100644
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
 ## [0.9.18] - [2019-05-18]

 ### Added
diff --git a/cloudfeaster/__init__.py b/cloudfeaster/__init__.py
index aefe3c8..47c3353 100644
--- a/cloudfeaster/__init__.py
+++ b/cloudfeaster/__init__.py
@@ -1 +1 @@
-__version__ = '0.9.18'
+__version__ = '0.9.19'
These changes to master for next release look ok? (y/n)>
```

```bash
[master 95b1090] Prep CHANGELOG.md for next release
 2 files changed, 15 insertions(+), 1 deletion(-)
Switched to branch 'release-0.9.18'
c8375269c2c749e59e22699c97842338
running bdist_wheel
running build
running build_py
creating build
creating build/lib.linux-x86_64-2.7
creating build/lib.linux-x86_64-2.7/cloudfeaster
copying cloudfeaster/spider.py -> build/lib.linux-x86_64-2.7/cloudfeaster
copying cloudfeaster/__init__.py -> build/lib.linux-x86_64-2.7/cloudfeaster
copying cloudfeaster/jsonschemas.py -> build/lib.linux-x86_64-2.7/cloudfeaster
creating build/lib.linux-x86_64-2.7/cloudfeaster/samples
copying cloudfeaster/samples/xe_exchange_rates.py -> build/lib.linux-x86_64-2.7/cloudfeaster/samples
copying cloudfeaster/samples/__init__.py -> build/lib.linux-x86_64-2.7/cloudfeaster/samples
copying cloudfeaster/samples/pythonwheels.py -> build/lib.linux-x86_64-2.7/cloudfeaster/samples
copying cloudfeaster/samples/pypi.py -> build/lib.linux-x86_64-2.7/cloudfeaster/samples
creating build/lib.linux-x86_64-2.7/cloudfeaster_extension
copying cloudfeaster_extension/__init__.py -> build/lib.linux-x86_64-2.7/cloudfeaster_extension
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
running build_scripts
creating build/scripts-2.7
copying bin/run-all-spiders.sh -> build/scripts-2.7
copying bin/run-spider.sh -> build/scripts-2.7
installing to build/bdist.linux-x86_64/wheel
running install
running install_lib
creating build/bdist.linux-x86_64
creating build/bdist.linux-x86_64/wheel
creating build/bdist.linux-x86_64/wheel/cloudfeaster
creating build/bdist.linux-x86_64/wheel/cloudfeaster/jsonschemas
copying build/lib.linux-x86_64-2.7/cloudfeaster/jsonschemas/spider_metadata.json -> build/bdist.linux-x86_64/wheel/cloudfeaster/jsonschemas
copying build/lib.linux-x86_64-2.7/cloudfeaster/jsonschemas/spider_output.json -> build/bdist.linux-x86_64/wheel/cloudfeaster/jsonschemas
copying build/lib.linux-x86_64-2.7/cloudfeaster/spider.py -> build/bdist.linux-x86_64/wheel/cloudfeaster
copying build/lib.linux-x86_64-2.7/cloudfeaster/__init__.py -> build/bdist.linux-x86_64/wheel/cloudfeaster
copying build/lib.linux-x86_64-2.7/cloudfeaster/jsonschemas.py -> build/bdist.linux-x86_64/wheel/cloudfeaster
creating build/bdist.linux-x86_64/wheel/cloudfeaster/samples
copying build/lib.linux-x86_64-2.7/cloudfeaster/samples/xe_exchange_rates.py -> build/bdist.linux-x86_64/wheel/cloudfeaster/samples
copying build/lib.linux-x86_64-2.7/cloudfeaster/samples/__init__.py -> build/bdist.linux-x86_64/wheel/cloudfeaster/samples
copying build/lib.linux-x86_64-2.7/cloudfeaster/samples/pythonwheels.py -> build/bdist.linux-x86_64/wheel/cloudfeaster/samples
copying build/lib.linux-x86_64-2.7/cloudfeaster/samples/pypi.py -> build/bdist.linux-x86_64/wheel/cloudfeaster/samples
creating build/bdist.linux-x86_64/wheel/cloudfeaster_extension
copying build/lib.linux-x86_64-2.7/cloudfeaster_extension/__init__.py -> build/bdist.linux-x86_64/wheel/cloudfeaster_extension
running install_egg_info
Copying cloudfeaster.egg-info to build/bdist.linux-x86_64/wheel/cloudfeaster-0.9.18.egg-info
running install_scripts
creating build/bdist.linux-x86_64/wheel/cloudfeaster-0.9.18.data
creating build/bdist.linux-x86_64/wheel/cloudfeaster-0.9.18.data/scripts
copying build/scripts-2.7/run-all-spiders.sh -> build/bdist.linux-x86_64/wheel/cloudfeaster-0.9.18.data/scripts
copying build/scripts-2.7/run-spider.sh -> build/bdist.linux-x86_64/wheel/cloudfeaster-0.9.18.data/scripts
changing mode of build/bdist.linux-x86_64/wheel/cloudfeaster-0.9.18.data/scripts/run-all-spiders.sh to 755
changing mode of build/bdist.linux-x86_64/wheel/cloudfeaster-0.9.18.data/scripts/run-spider.sh to 755
creating build/bdist.linux-x86_64/wheel/cloudfeaster-0.9.18.dist-info/WHEEL
running sdist
running check
creating cloudfeaster-0.9.18
creating cloudfeaster-0.9.18/bin
creating cloudfeaster-0.9.18/cloudfeaster
creating cloudfeaster-0.9.18/cloudfeaster.egg-info
creating cloudfeaster-0.9.18/cloudfeaster/jsonschemas
creating cloudfeaster-0.9.18/cloudfeaster/samples
creating cloudfeaster-0.9.18/cloudfeaster_extension
making hard links in cloudfeaster-0.9.18...
hard linking MANIFEST.in -> cloudfeaster-0.9.18
hard linking README.rst -> cloudfeaster-0.9.18
hard linking setup.cfg -> cloudfeaster-0.9.18
hard linking setup.py -> cloudfeaster-0.9.18
hard linking bin/run-all-spiders.sh -> cloudfeaster-0.9.18/bin
hard linking bin/run-spider.sh -> cloudfeaster-0.9.18/bin
hard linking cloudfeaster/__init__.py -> cloudfeaster-0.9.18/cloudfeaster
hard linking cloudfeaster/jsonschemas.py -> cloudfeaster-0.9.18/cloudfeaster
hard linking cloudfeaster/spider.py -> cloudfeaster-0.9.18/cloudfeaster
hard linking cloudfeaster.egg-info/PKG-INFO -> cloudfeaster-0.9.18/cloudfeaster.egg-info
hard linking cloudfeaster.egg-info/SOURCES.txt -> cloudfeaster-0.9.18/cloudfeaster.egg-info
hard linking cloudfeaster.egg-info/dependency_links.txt -> cloudfeaster-0.9.18/cloudfeaster.egg-info
hard linking cloudfeaster.egg-info/requires.txt -> cloudfeaster-0.9.18/cloudfeaster.egg-info
hard linking cloudfeaster.egg-info/top_level.txt -> cloudfeaster-0.9.18/cloudfeaster.egg-info
hard linking cloudfeaster/jsonschemas/spider_metadata.json -> cloudfeaster-0.9.18/cloudfeaster/jsonschemas
hard linking cloudfeaster/jsonschemas/spider_output.json -> cloudfeaster-0.9.18/cloudfeaster/jsonschemas
hard linking cloudfeaster/samples/__init__.py -> cloudfeaster-0.9.18/cloudfeaster/samples
hard linking cloudfeaster/samples/pypi.py -> cloudfeaster-0.9.18/cloudfeaster/samples
hard linking cloudfeaster/samples/pythonwheels.py -> cloudfeaster-0.9.18/cloudfeaster/samples
hard linking cloudfeaster/samples/xe_exchange_rates.py -> cloudfeaster-0.9.18/cloudfeaster/samples
hard linking cloudfeaster_extension/__init__.py -> cloudfeaster-0.9.18/cloudfeaster_extension
copying setup.cfg -> cloudfeaster-0.9.18
Writing cloudfeaster-0.9.18/setup.cfg
Creating tar archive
removing 'cloudfeaster-0.9.18' (and everything under it)
diff --git a/README.md b/README.md
index 61aaccd..3599633 100644
--- a/README.md
+++ b/README.md
@@ -5,7 +5,7 @@
 ![status](https://img.shields.io/pypi/status/cloudfeaster.svg?style=flat)
 [![PyPI](https://img.shields.io/pypi/v/cloudfeaster.svg?style=flat)](https://pypi.python.org/pypi/cloudfeaster)
 [![Requirements](https://requires.io/github/simonsdave/cloudfeaster/requirements.svg?branch=master)](https://requires.io/github/simonsdave/cloudfeaster/requirements/?branch=master)
-[![CircleCI](https://circleci.com/gh/simonsdave/cloudfeaster/tree/master.svg?style=shield)](https://circleci.com/gh/simonsdave/cloudfeaster/tree/master)
+[![CircleCI](https://circleci.com/gh/simonsdave/cloudfeaster/tree/release-0.9.18.svg?style=shield)](https://circleci.com/gh/simonsdave/cloudfeaster/tree/release-0.9.18)
 [![Coverage Status](https://coveralls.io/repos/simonsdave/cloudfeaster/badge.svg?style=flat)](https://coveralls.io/r/simonsdave/cloudfeaster)
 [![docker-simonsdave/cloudfeaster-xenial-dev-env](https://img.shields.io/badge/dockerhub-simonsdave%2Fcloudfeaster--xenial--dev-blue.svg)](https://hub.docker.com/r/simonsdave/cloudfeaster-xenial-dev-env)
@@ -16,13 +16,13 @@ modern software engineering tools, services and trends to create:
 * (this repo is) [a spider authoring and maintenance environment](https://github.com/simonsdave/cloudfeaster)
 * a service infrastructure for discovering and running spiders via a RESTful API

-[This](docs/story.md) is the story behind Cloudfeaster.
+[This](https://github.com/simonsdave/cloudfeaster/tree/release-0.9.18/docs/story.md) is the story behind Cloudfeaster.

 ## What Next

-* [this](docs/spider_authors.md) describes
+* [this](https://github.com/simonsdave/cloudfeaster/tree/release-0.9.18/docs/spider_authors.md) describes
 how to author spiders using Cloudfeaster
-* see [these](docs/contributing.md) instructions
+* see [these](https://github.com/simonsdave/cloudfeaster/tree/release-0.9.18/docs/contributing.md) instructions
 describe how to setup your development environment and
 start contributing to Cloudfeaster
 * take a look at these sample spiders
These changes to release-0.9.18 look ok? (y/n)>
```

```bash
Switched to branch 'master'
Your branch is ahead of 'origin/master' by 2 commits.
  (use "git push" to publish your local commits)
Counting objects: 8, done.
Delta compression using up to 12 threads.
Compressing objects: 100% (7/7), done.
Writing objects: 100% (8/8), 728 bytes | 728.00 KiB/s, done.
Total 8 (delta 5), reused 0 (delta 0)
remote: Resolving deltas: 100% (5/5), completed with 3 local objects.
To github.com:simonsdave/cloudfeaster.git
   41224c8..95b1090  master -> master
Switched to branch 'release-0.9.18'
Counting objects: 3, done.
Delta compression using up to 12 threads.
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 351 bytes | 351.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0)
remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
remote:
remote: Create a pull request for 'release-0.9.18' on GitHub by visiting:
remote:      https://github.com/simonsdave/cloudfeaster/pull/new/release-0.9.18
remote:
To github.com:simonsdave/cloudfeaster.git
 * [new branch]      release-0.9.18 -> release-0.9.18
Switched to branch 'master'
Your branch is up to date with 'origin/master'.
(env) ~>
```

```bash
(env) ~> upload-dist-to-pypi.sh testpypi
Uploading distributions to https://test.pypi.org/legacy/
Uploading cloudfeaster-0.9.18-py2-none-any.whl
100%|##########| 26.7k/26.7k [00:03<00:00, 8.72kB/s]
Uploading cloudfeaster-0.9.18.tar.gz
100%|##########| 22.1k/22.1k [00:01<00:00, 12.3kB/s]
(env) ~>
```

Now look on [https://test.pypi.org/project/cloudfeaster/](https://test.pypi.org/project/cloudfeaster/)
to confirm all is ok and if it is upload to the test version of pypi.

```bash
(env) ~> upload-dist-to-pypi.sh pypi
Uploading distributions to https://upload.pypi.org/legacy/
Uploading cloudfeaster-0.9.18-py2-none-any.whl
100%|##########| 26.7k/26.7k [00:02<00:00, 12.1kB/s]
Uploading cloudfeaster-0.9.18.tar.gz
100%|##########| 22.1k/22.1k [00:02<00:00, 10.8kB/s]
(env) ~>
```

Now look on [https://pypi.org/project/cloudfeaster/](https://pypi.org/project/cloudfeaster/)
to confirm all is ok and if it is upload to the production version of pypi.

## What Next

* start contributing!
