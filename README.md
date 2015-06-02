# Beta402 - DocHub


Beta402 or DocHub is a website, written in django. It's main goal is to provide a space for students (for now form the [ULB](http://ulb.ac.be) univeristy) to collaborate, help each other and distribute old exams and exercices.

There is a [live instance of DocHub](http://dochub.be) hosted by UrLab and the Cercle-Informatique.

## Screenshots

![](https://github.com/urlab/beta402/blob/master/.meta/screen-1.png)
![](https://github.com/urlab/beta402/blob/master/.meta/screen-2.png)
![](https://github.com/urlab/beta402/blob/master/.meta/screen-3.png)

## Tech

### Dependencies

You'll need everything that is in requirements.txt (don't worry, pip will do it for you).

You will also need to install poppler (the binary 'pdftotext'), GraphicsMagick (the binary 'gm') and LibreOffice/OpenOffice + unoconv (you need the binary 'unoconv') using your distribution packages.

For exemple on Debian/Ubuntu

    sudo apt-get install poppler-utils graphicsmagick unoconv python-dev libjpeg8-dev

Or on Fedora

    sudo yum install poppler-utils GraphicsMagick unoconv python-devel libjpeg-devel

### Installation

    # Install dependencies then
    make install database

### Run

    honcho start

Then go http://localhost:8000/

### Reset

    make cleandata database


### Misc


Add another user to the db

    ./manage.py useradd


## Contribute !


Come by #urlab on freenode or just fork this repo and send a patch !


## License


Copyright 2012 - 2015, Cercle Informatique ASBL. All rights reserved.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This software was made by hast, C4, iTitou at UrLab, ULB's hackerspace


[_Woop woop_](https://www.youtube.com/watch?v=z13qnzUQwuI)

