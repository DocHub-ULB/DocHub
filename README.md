Beta402
=======

This django project is a website providing mean for students to exchange courses and tips.
Some old code is already live over there : http://cours.cerkinfo.be

Dependencies
============

You'll need everything that is in requirements.txt (don't worry, pip will do it for you).

You will also need to install poppler (the binary 'pdftotext'), GraphicsMagick (the binary 'gm') and LibreOffice/OpenOffice + unoconv (you need the binary 'unoconv') using your distribution packages.

For exemple:

    sudo apt-get install poppler-utils graphicsmagick unoconv

Installation
============

		sudo apt-get install python-dev
		make ve
		source ve/bin/activate
		make install

Run & Stop
==========

		make [run]
		make stop

Then go http://localhost:8000/syslogin

Reset
=====

		make clean


Misc
====

Add another user to the db
--------------------------

	./manage.py useradd

Speed up the conversion process (optional)
-------------------------------

We use `unoconv` to convert files to pdf. To speed up the process, just run somwhere in the background (screen, supervisord, background shell, whatever) `unoconv -l` which will start a conversion server and all tasks will be sent there so that we will not boot OpenOffice at every new conversion.

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

