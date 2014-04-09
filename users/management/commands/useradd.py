# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from django.core.management.base import BaseCommand
from users.models import User
from getpass import getpass, getuser
from optparse import make_option


class Command(BaseCommand):
    help = 'Initialize fognar for developpment'
    option_list = BaseCommand.option_list + (
        make_option('--netid', action='store', dest='netid', default=None, help='default netid'),
        make_option('--password', action='store', dest='password', default=None, help='default password'),
        make_option('--first-name', action='store', dest='first_name', default=None, help='default first name'),
        make_option('--last-name', action='store', dest='last_name', default=None, help='default last name'),
    )

    def handle(self, *args, **options):
        self.stdout.write('Creating user\n')
        user = User()
        netid = raw_input("Username (default: %s): " % getuser()) if options["netid"] is None else options["netid"]
        if not netid:
            netid = getuser()
        user.netid = netid
        password = getpass("Password (default: 'test'): ") if options["password"] is None else options["password"]
        if not password:
            password = 'test'
        first_name = raw_input("Firstname (default: John): ") if options["first_name"] is None else options["first_name"]
        if not first_name:
            first_name = "John"
        last_name = raw_input("Lastname (default: Smith): ") if options["last_name"] is None else options["last_name"]
        if not last_name:
            last_name = "Smith"
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.email = 'test@mouh.com'
        user.save()
        print "User id : " + str(user.id)
