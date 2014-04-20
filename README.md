CloudFeaster is a screen scraping infrastructure that dramatically
simplifies the creation and operation of spiders that login to web
sites on behalf of consumers.
[Why another screen scraping tool when lots already exist?](https://github.com/simonsdave/clf/wiki/FAQ#lots-of-screen-scraping-utilities-exist-why-create-another-one)

Prerequisites 
-------------
* code written and tested on Mac OS X:
  * [git](http://git-scm.com/) 
  * [Python](http://www.python.org/) 
  * [pip](http://www.pip-installer.org/en/latest/installing.html)
  * [virtualenv](https://pypi.python.org/pypi/virtualenv)
  * [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
  * [Vagrant](http://downloads.vagrantup.com)
  * [ChromeDriver](http://chromedriver.storage.googleapis.com/index.html)
  * [Command Line Tools for Xcode](https://developer.apple.com/downloads/index.action)
* see
[requirements.txt](https://github.com/simonsdave/clf/blob/master/requirements.txt "requirements.txt")
for the complete list of Python packages on which CloudFeaster depends

Development
-----------
The following (brief) instructions describe how to setup a your development environment
on Mac OS X.

> Before you start working through the instructions below make sure you
> have installed the components described above. In particular, if you don't install
> [Command Line Tools for Xcode](https://developer.apple.com/downloads/index.action)
> you'll find it hard to debug the error messages produced by
> [source bin/cfg4dev](bin/cfg4dev). 

* get the source code by running the following in a new terminal window

~~~~~
cd
git clone https://github.com/simonsdave/clf.git
cd clf
source bin/cfg4dev
~~~~~

* both unit and integration tests are executed using
[nose](http://nose.readthedocs.org/en/latest/)
* all integration tests are tagged with the
[attr](http://nose.readthedocs.org/en/latest/plugins/attrib.html) *integration*
* to execute all unit tests go to clf's root directory and run

~~~~~
nosetests -A "not integration"
~~~~~

* to execute all integration tests go to clf's root directory and run

~~~~~
nosetests -A "integration"
~~~~~

* and, of course, to execute all tests go to clf's root directory and run

~~~~~
nosetests
~~~~~

