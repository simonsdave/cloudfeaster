#Contributing
The following instructions describe how to setup a your development environment on Mac OS X.

Install
[Command Line Tools for Xcode](https://developer.apple.com/downloads/index.action)
otherwise you'll find it hard to debug the error messages produced by
during ```source cfg4dev```.

Get the source code and configure the development environment
by running the following in a new terminal window

```bash
>cd
>git clone https://github.com/simonsdave/clf.git
>cd clf
>source cfg4dev
<<<snip lots>>>
(env)>
```

Both unit and integration tests are executed using
[nose](http://nose.readthedocs.org/en/latest/).
All integration tests are tagged with the
[attr](http://nose.readthedocs.org/en/latest/plugins/attrib.html) ```integration```.

To run all tests go to clf's root directory and run

```bash
(env)>nosetests
.......................................................................................................................................
----------------------------------------------------------------------
Ran 135 tests in 92.139s

OK
(env)>
```

To execute just unit tests go to clf's root directory and run

```bash
(env)>nosetests -A "not integration"
....................................................................................................................
----------------------------------------------------------------------
Ran 116 tests in 0.886s

OK
(env)>
```

To execute all integration tests go to clf's root directory and run

```bash
(env)>nosetests -A "integration"
...................
----------------------------------------------------------------------
Ran 19 tests in 90.787s

OK
(env)>
```
