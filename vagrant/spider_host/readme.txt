export DISPLAY=:99
Xvfb :99 -ac -screen 0 1280x1024x24 >& /dev/null &

git clone https://github.com/simonsdave/clf.git
cd clf
source bin/cfg4dev
cd /vagrant
~/clf/bin/things_generally_working.py

Getting Xvfb to start upon booting system in Ubuntu Maverick
    http://serverfault.com/questions/251961/getting-xvfb-to-start-upon-booting-system-in-ubuntu-maverick

Upstart Intro, Cookbook and Best Practises
    http://upstart.ubuntu.com/
    http://upstart.ubuntu.com/cookbook/#what-is-upstart
    current "state of the art" for Ubuntu daemon process management
    Ubuntu Daemon Best Practices?
        http://serverfault.com/questions/287277/ubuntu-daemon-best-practices

what is start-stop-daemon in linux scripting?
    http://stackoverflow.com/questions/16139940/what-is-start-stop-daemon-in-linux-scripting

docker
    http://www.docker.io/
    http://docs.docker.io/en/latest/use/basics/

Python: Starting Tornado Apps at Boot Using Upstart
    http://www.charleshooper.net/blog/python-starting-tornado-apps-at-boot-using-upstart/

Linux: How to measure actual memory usage of an application or process?
    http://stackoverflow.com/questions/131303/linux-how-to-measure-actual-memory-usage-of-an-application-or-process
