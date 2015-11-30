# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from users.models import User
from getpass import getpass, getuser
from optparse import make_option


class Command(BaseCommand):
    help = 'Create a new normal user'
    option_list = BaseCommand.option_list + (
        make_option('--netid', action='store', dest='netid', default=None),
        make_option('--password', action='store', dest='password', default=None),
        make_option('--first-name', action='store', dest='first_name', default=None),
        make_option('--last-name', action='store', dest='last_name', default=None),
    )

    def handle(self, *args, **options):
        netid = raw_input("Username (default: %s): " % getuser()) if options["netid"] is None else options["netid"]
        if not netid:
            netid = getuser()

        password = getpass("Password (default: 'test'): ") if options["password"] is None else options["password"]
        if not password:
            password = 'test'

        first_name = raw_input("Firstname (default: John): ") if options["first_name"] is None else options["first_name"]
        if not first_name:
            first_name = "John"

        last_name = raw_input("Lastname (default: Smith): ") if options["last_name"] is None else options["last_name"]
        if not last_name:
            last_name = "Smith"

        email = '{}@fake.ulb.ac.be'.format(netid)

        try:
            user = User.objects.create_user(netid=netid, email=email, password=password, first_name=first_name, last_name=last_name)
            self.stdout.write('User created: {}\n'.format(repr(user)))
        except IntegrityError as e:
            self.stdout.write("Error:\n")
            self.stdout.write(str(e))
