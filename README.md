# DocHub

[![License](https://img.shields.io/badge/license-AGPL%20v3-blue.svg)](https://github.com/UrLab/beta402/blob/master/LICENSE)

DocHub is a website, written in django. It's main goal is to provide a space for students (for now form the [ULB](https://ulb.ac.be) university) to collaborate, help each other and distribute old exams and exercices.

There is a [live instance of DocHub](https://dochub.be) hosted by [UrLab](https://urlab.be) and the [Cercle Informatique](https://cerkinfo.be).

## Screenshots

![](https://github.com/urlab/dochub/blob/master/.meta/screen-1.png)
![](https://github.com/urlab/dochub/blob/master/.meta/screen-2.png)
![](https://github.com/urlab/dochub/blob/master/.meta/screen-3.png)

## Tech

DocHub currently (Feb 2021) runs with Python 3.8, ~~Node 10~~ and Postgresql 12.

### Dependencies

```console
# Ubuntu
sudo apt-get install unoconv python3-dev ruby libtiff5-dev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk mupdf-tools
# Fedora
sudo dnf install unoconv python-devel ruby mupdf
# Arch linux
sudo pacman -S unoconv ruby python mupdf-tools
```

### Installation

```console
make install database
```

### Run

```console
./manage.py runserver
```

Then go http://localhost:8000/

There will already be 2 users in the database, both with `test` as a password:

- $(USER) : your username on your machine
- blabevue

### Misc

#### Add another user to the db

```console
./manage.py createuser
```

#### Requirements

To add a requirement, write it in `requirements.in` file, and generate the requirements.txt file with the following command

```console
pip-compile
```

## Testing

Run only fast tests (total time < 2 sec) : not testing actual file conversions

```console
py.test -k "not slow"
```

Run all tests (~20 sec)

```console
py.test
```

## Contribute !

Come by #urlab on freenode or just fork this repo and submit a PR !

## License

Copyright 2012 - 2021, Cercle Informatique ASBL. All rights reserved.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This software was made by hast, C4, ititou and rom1 at UrLab (https://urlab.be): ULB's hackerspace

[_Woop woop_](https://www.youtube.com/watch?v=SxSLU2-ERpk)
