CloudFeaster is a screen scraping infrastructure that dramatically
simplifies the creation and operation of spiders that login to web
sites on behalf of consumers.

Lots of
[screen scraping utilities](https://github.com/simonsdave/clf/wiki/Other-Web-Scraping-Utilities-&-Approaches)
exist so why create another one?
Three primary reasons:

1. the other 
[screen scraping utilities](https://github.com/simonsdave/clf/wiki/Other-Web-Scraping-Utilities-&-Approaches)
are general purpose tools where as CloudFeaster is specialized for
the task of creating spiders that login to web
sites on behalf of consumers
1. CloudFeaster is not a single tool or utility; CloudFeaster is
a complete end-to-end infrastructure supporting the creation and
operation spiders
1. CloudFeaster thinks about the problem very differently and
leverages modern approaches to software engineering

Prerequisites 
-------------
* code written and tested on Mac OS X 10.8.4 using
  * [VirtualBox 4.2.18](https://www.virtualbox.org/wiki/Downloads)
  * [Vagrant 1.3.4](http://downloads.vagrantup.com/tags/v1.3.4)
  * [ChromeDriver 2.4](http://chromedriver.storage.googleapis.com/index.html?path=2.4/)
  * [git 1.7.12.4](http://git-scm.com/)
  * [Python 2.7.2](http://www.python.org/)
  * [virtualenv 1.9.1](https://pypi.python.org/pypi/virtualenv)
  * [command line tools (OS X Mountain Lion) for Xcode - April 2013](https://developer.apple.com/downloads/index.action)
* see
[requirements.txt](https://github.com/simonsdave/clf/blob/master/requirements.txt "requirements.txt")
for the complete list of python packages on which CloudFeaster depends

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
cd clf
source bin/cfg4dev
~~~~~

* ...
