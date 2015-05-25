#Using
:TODO:

```bash
>gcloud compute instances create dave --machine-type n1-standard-1 --image ubuntu-14-04
>gcloud compute ssh dave

from http://www.ubuntuupdates.org/ppa/google_chrome?dist=stable
* wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 
* sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
* sudo apt-get update 
* sudo apt-get install -y google-chrome-stable

dave@dave:~$ which google-chrome
/usr/bin/google-chrome
dave@dave:~$

sudo apt-get install -y xvfb

sudo apt-get install -y unzip
curl -s --output chromedriver.zip http://chromedriver.storage.googleapis.com/2.15/chromedriver_linux64.zip
unzip chromedriver.zip
rm chromedriver.zip
sudo mv chromedriver /usr/bin/.
sudo chown root.root /usr/bin/chromedriver
sudo chmod a+wrx /usr/bin/chromedriver

sudo apt-get update
dave@dave:~$ sudo apt-get install -y git
sudo apt-get install -y python-virtualenv
# sudo apt-get install -y python-pip
sudo apt-get install -y python-dev

git clone https://github.com/simonsdave/cloudfeaster.git
cd cloudfeaster
```

```bash
>docker run -i -t cloudfeaster_dev /bin/bash
root@176cd3b223e5:/# git clone https://github.com/simonsdave/cloudfeaster.git
root@176cd3b223e5:/# cd cloudfeaster
root@176cd3b223e5:/# source cfg4dev
root@176cd3b223e5:/# nosetests
```

```bash
docker rm `docker ps --no-trunc -a -q`
```

```bash
>lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 14.04.2 LTS
Release:    14.04
Codename:   trusty
```

https://docs.docker.com/userguide/dockerrepos/
