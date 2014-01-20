initctl list | grep clf

sudo service clf-xvfb start
sudo service clf-spider-host start

/var/log/upstart/clf-spider-host.log
/var/log/upstart/clf-xvfb.log

ps aux | grep [X]vfb
ps aux | grep [s]pider

Getting Xvfb to start upon booting system in Ubuntu Maverick
    http://serverfault.com/questions/251961/getting-xvfb-to-start-upon-booting-system-in-ubuntu-maverick

Upstart Intro, Cookbook and Best Practises
    http://upstart.ubuntu.com/
    http://upstart.ubuntu.com/cookbook/#what-is-upstart
    current "state of the art" for Ubuntu daemon process management
    Ubuntu Daemon Best Practices?
        http://serverfault.com/questions/287277/ubuntu-daemon-best-practices
    Awesome basics post:
        http://stackoverflow.com/questions/17747605/daemon-vs-upstart-for-python-script

what is start-stop-daemon in linux scripting?
    http://stackoverflow.com/questions/16139940/what-is-start-stop-daemon-in-linux-scripting

docker
    http://www.docker.io/
    http://docs.docker.io/en/latest/use/basics/

Python: Starting Tornado Apps at Boot Using Upstart
    http://www.charleshooper.net/blog/python-starting-tornado-apps-at-boot-using-upstart/

Linux: How to measure actual memory usage of an application or process?
    http://stackoverflow.com/questions/131303/linux-how-to-measure-actual-memory-usage-of-an-application-or-process
