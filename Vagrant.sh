set -v
apt-get install -y graphicsmagick unoconv python-dev nodejs ruby npm python-pip python-virtualenv git
apt-get install -y libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
gem install sass
npm install -g yuglify
cd /vagrant
make install database
