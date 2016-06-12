#Contributing
The following instructions describe how to setup a your development
environment on Mac OS X.

# Getting Started

Install
[Command Line Tools for Xcode](https://developer.apple.com/downloads/index.action)
otherwise you'll find it hard to debug the error messages produced by
during ```source cfg4dev```.

Get the source code and configure the development environment
by running the following in a new terminal window

```bash
>cd
>git clone https://github.com/simonsdave/cloudfeater.git
>cd cloudfeaster
>source cfg4dev
<<<snip lots>>>
(env)>
```

Both unit and integration tests are executed using
[nose](http://nose.readthedocs.org/en/latest/).
All integration tests are tagged with the
[attr](http://nose.readthedocs.org/en/latest/plugins/attrib.html) ```integration```.

To run all tests go to cloudfeaster's root directory and run

```bash
(env)>nosetests
.......................................................................................................................................
----------------------------------------------------------------------
Ran 135 tests in 92.139s

OK
(env)>
```

To execute just unit tests go to cloudfeaster's root directory and run

```bash
(env)>nosetests -A "not integration"
....................................................................................................................
----------------------------------------------------------------------
Ran 116 tests in 0.886s

OK
(env)>
```

To execute all integration tests go to cloudfeaster's root directory and run

```bash
(env)>nosetests -A "integration"
...................
----------------------------------------------------------------------
Ran 19 tests in 90.787s

OK
(env)>
```

# User Agent Headers

How do I find out the user agent header?
Try [this](http://www.whoishostingthis.com/tools/user-agent/) web site.

# Google Chrome Version

How do I figure out what version of Chrome I'm using?
On Ubuntu try ```google-chrome --version```.

# Coverage Report

How can I generate a coverage report?
From Cloudfeaster's root directory run the following:
~~~~~
coverage erase
rm -rf ./coverage_report/
nosetests --with-coverage
coverage html
~~~~~
An HTML version of the coverage report can now be found in coverage_report/index.html
