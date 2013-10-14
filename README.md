CloudFeaster is a web automation infrastructure.

Prerequisites 
-------------
* code written and tested on Mac OS X 10.8.4 using
[git 1.7.12.4](http://git-scm.com/),
[Python 2.7.2](http://www.python.org/),
[virtualenv 1.9.1](https://pypi.python.org/pypi/virtualenv),
and
[command line tools (OS X Mountain Lion) for Xcode - April 2013](https://developer.apple.com/downloads/index.action)
* see
[requirements.txt](https://github.com/simonsdave/clf/blob/master/requirements.txt "requirements.txt")
for the complete list of python packages on which yar depends

Development
-----------
The following (brief) instructions describe how to setup a your development environment.

> Before you start working through the instructions below make sure you
> have installed the components described above. In particular, if you don't install
> [command line tools (OS X Mountain Lion) for Xcode - April 2013](https://developer.apple.com/downloads/index.action)
> you'll find it hard to debug the error messages produced by
> [source bin/cfg4dev](https://github.com/simonsdave/clf/blob/master/bin/cfg4dev). 

* get the source code by running the following in a new terminal window

~~~~~
cd
git clone https://github.com/simonsdave/clf.git
cd mvmd
source bin/cfg4dev
~~~~~

* ...
