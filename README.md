Beta402
=======

This django project is a website providing mean for students to exchange courses and tips.
Some old code is already live over there : http://cours.cerkinfo.be

Dependencies
============

You'll need everything that is in requirements.txt (don't worry, pip will do it for you).

You will also need to install poppler (the binary 'pdftotext') and GraphicsMagick (the binary 'gm') using your distribution packages.

For exemple:

    sudo apt-get install poppler-utils graphicsmagick

Installation
============
	
		make ve
		source ve/bin/activate
		make install

Run & Stop
==========

		make [run]
		make stop
		
Reset
=====
		
		make clean

Then go http://localhost:8000/syslogin

Misc
====

Add another user to the db
--------------------------

	./manage.py adduser

Contribute !
------------

Send an email to p402 AT cerkinfo.be, come by #urlab on freenode or just fork this repo and send a patch !


License
=======

Copyright 2011-2013, hast. All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.


Woop woop https://www.youtube.com/watch?v=x2FetnIZjxg

