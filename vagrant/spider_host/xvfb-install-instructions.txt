export DISPLAY=:99
Xvfb :99 -ac -screen 0 1280x1024x24 >& /dev/null &

git clone https://github.com/simonsdave/clf.git
cd clf
source bin/cfg4dev
cd /vagrant
~/clf/bin/things_generally_working.py
