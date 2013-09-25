# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import json
from BeautifulSoup import BeautifulSoup

data = {}
a = 0
total = len(os.listdir("./cours/"))
for cours in os.listdir("./cours/"):
    a += 1
    sys.stdout.write("%s/%s\r" % (a, total))
    sys.stdout.flush()
    data[cours] = {}
    soup = BeautifulSoup(open("./cours/" + cours).read())
    if soup.find('table', 'bordertable') is None:
        continue
    for line in filter(lambda x: len(x('td')) == 2 and x.td.text, soup.find('table', 'bordertable')('tr')):
        key, value = line('td')
        data[cours][key.text] = value.text

sys.stdout.write("\n")
open("cours.json", "w").write(json.dumps(data))