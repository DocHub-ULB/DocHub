FROM django:onbuild
# FOR DEV ONLY - DO NOT USE IN PRODUCTION WITHOUT A PROPER BACKEND INCLUDING GUNICORN AND FRIENDS

# who are we ?
MAINTAINER UrLab

# Add the path
ADD . /usr/src/app

# Update the default application repository sources list
RUN apt-get update && apt-get -y upgrade

# Install the packages needed
RUN apt-get install -y graphicsmagick unoconv python-dev nodejs ruby npm python-pip python-virtualenv git make
RUN apt-get install -y libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
RUN gem install sass
RUN npm install -g yuglify

# DB
ENV USER=netid
RUN make install database
