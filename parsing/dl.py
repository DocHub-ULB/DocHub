# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import requests
from furl import furl
from urlparse import parse_qs
from BeautifulSoup import BeautifulSoup

#result = requests.get('http://banssbfr.ulb.ac.be/PROD_frFR/bzscrse.p_prog_catalog', data={"lang": "FRENCH", "term_in": "201213", "attrib_in": "ALL", "submit_btn": "Soumettre"})
result = requests.get("http://banssbfr.ulb.ac.be/PROD_frFR/bzscrse.p_prog_catalog?lang=FRENCH&term_in=201213&college_in=&level_in=&attrib_in=ALL")

soup = BeautifulSoup(result.content)

a = 0
total = len(map(lambda x: x.a['href'], soup('table', 'dataentrytable')[-1]('td')))

for url in map(lambda x: x.a['href'], soup('table', 'dataentrytable')[-1]('td')):
    a += 1
    soupsoup = BeautifulSoup(requests.get("http://banssbfr.ulb.ac.be/PROD_frFR/" + url).content)
    #print "on", "http://banssbfr.ulb.ac.be/PROD_frFR/" + url
    b = 0
    total2 = len(filter(lambda x: x.get("href") and "pname=PPROGCODE" in x["href"], soupsoup('a')))
    for line in filter(lambda x: x.get("href") and "pname=PPROGCODE" in x["href"], soupsoup('a')):
        b += 1
        #print "    find", line["href"]
        course_url = furl(line["href"])
        identifier = sorted(parse_qs(line["href"])["pvalue"])
        if os.path.exists("dumps/" + "_".join(identifier)):
            sys.stdout.write("%s/%s %s/%s\r" % (b, total2, a, total))
            sys.stdout.flush()
            continue
        to_write = requests.get("http://banssbfr.ulb.ac.be/PROD_frFR/" + line["href"]).content
        open("catalogs/" + "_".join(identifier), "w").write(to_write)

        sys.stdout.write("%s/%s %s/%s\r" % (b, total2, a, total))
        sys.stdout.flush()

sys.stdout.write("\n")