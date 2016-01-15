# Beta402 - DocHub

[![Build Status](https://travis-ci.org/UrLab/beta402.svg?branch=master)](https://travis-ci.org/UrLab/beta402) [![Coverage Status](https://coveralls.io/repos/UrLab/beta402/badge.svg?branch=master&service=github)](https://coveralls.io/github/UrLab/beta402?branch=master) [![License](https://img.shields.io/badge/license-AGPL%20v3-blue.svg)](https://github.com/UrLab/beta402/blob/master/LICENSE)


Beta402 or DocHub is a website, written in django. It's main goal is to provide a space for students (for now form the [ULB](http://ulb.ac.be) univeristy) to collaborate, help each other and distribute old exams and exercices.

There is a [live instance of DocHub](http://dochub.be) hosted by [UrLab](http://urlab.be) and the [Cercle Informatique](http://cerkinfo.be).

## Screenshots

![](https://github.com/urlab/beta402/blob/master/.meta/screen-1.png)
![](https://github.com/urlab/beta402/blob/master/.meta/screen-2.png)
![](https://github.com/urlab/beta402/blob/master/.meta/screen-3.png)

## Tech

### Dependencies

    # Ubuntu
    sudo apt-get install graphicsmagick unoconv python-dev nodejs ruby
    # Feodra
    sudo dnf install GraphicsMagick unoconv python-devel nodejs ruby

### Installation

    gem install sass
    sudo npm install -g yuglify
    make install database

    If you don't want to run npm as root (we could understand), just run `npm install yuglify` and add the `yuglify` binary to your path. (it might be `/usr/local/bin/yuglify` or `./node_modules/.bin/yuglify` depending on your distro)

### Run

    honcho start

Then go http://localhost:8000/

There will already be 2 users in the database, both with `test` as a password:
   - $(USER) : your username on your machine
   - blabevue


### Misc


Add another user to the db

    ./manage.py createuser

## Testing

Run only fast tests (total time < 2 sec) : not testing actual file conversions

    py.test -k "not slow"

Run all tests (~20 sec)

    py.test

## Contribute !


Come by #urlab on freenode or just fork this repo and send a patch !


## License


Copyright 2012 - 2015, Cercle Informatique ASBL. All rights reserved.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace


[_Woop woop_](https://www.youtube.com/watch?v=z13qnzUQwuI)

