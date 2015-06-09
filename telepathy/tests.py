# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014-2015, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from django.test import TestCase
from .templatetags.custommardown import youtube_url


class MarkupTest(TestCase):
    def test_youtube_url(self):
        assert youtube_url.match("https://www.youtube.com/watch?v=TluTv5V0RmE&list=PLUl4u3cNGP60A3XMwZ5sep719_nh95qOe&index=5")
        assert youtube_url.match("https://youtube.com/watch?v=TluTv5V0RmE&list=PLUl4u3cNGP60A3XMwZ5sep719_nh95qOe&index=5")
        assert youtube_url.match("https://www.youtube.com/watch?v=0-CwXKrRCF0")
        assert youtube_url.match("https://www.youtube.com/watch?v=pJfDnJtsxc4")
        assert youtube_url.match("https://youtu.be/pJfDnJtsxc4?t=2s")
