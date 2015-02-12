Beta402
=======

This django project is a website providing mean for students to exchange courses and tips.
Some old code is already live over there : http://cours.cerkinfo.be

Dependencies
============

You'll need everything that is in requirements.txt (don't worry, pip will do it for you).

You will also need to install poppler (the binary 'pdftotext'), GraphicsMagick (the binary 'gm') and LibreOffice/OpenOffice + unoconv (you need the binary 'unoconv') using your distribution packages.

For exemple:

	# Debian/Ubuntu
    sudo apt-get install poppler-utils graphicsmagick unoconv python-dev

    # Fedora
    sudo apt-get install poppler-utils GraphicsMagick unoconv python-devel

Installation
============

        # Install dependencies then
		make install database

Run
==========

		honcho start

Then go http://localhost:8000/

Reset
=====

		make cleandata database


Misc
====

Add another user to the db
--------------------------

	./manage.py useradd


Contribute !
------------

Send an email to p402 AT cerkinfo.be, come by #urlab on freenode or just fork this repo and send a patch !


License
=======

Copyright 2014, Cercle Informatique ASBL. All rights reserved.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This software was made by hast, C4, iTitou at UrLab, ULB's hackerspace


Woop woop https://www.youtube.com/watch?v=x2FetnIZjxg

