import os
import sys
import requests
from urlparse import parse_qs
from BeautifulSoup import BeautifulSoup

count = set()

a = 0
for catalog in os.listdir('./catalogs/'):
    soup = BeautifulSoup(open("./catalogs/" + catalog, "r").read())
    for cours in filter(lambda x: x.nextSibling, soup('a', 'leaf')):
        cours_url = cours.nextSibling["href"]
        cours_args = parse_qs(cours.nextSibling["href"])
        cours_identifiant = "_".join((cours_args["subj_code_in"][0], cours_args["crse_numb_in"][0]))
        if cours_identifiant not in count:
            a += 1
            sys.stdout.write("%s\r" % a)
            sys.stdout.flush()
            count.add(cours_identifiant)
            if os.path.exists("cours/" + cours_identifiant):
                continue
            to_write = requests.get("http://banssbfr.ulb.ac.be/PROD_frFR/" + cours_url).content
            open("cours/" + cours_identifiant, "w").write(to_write)
        #from ipdb import set_trace; set_trace()

sys.stdout.write("\n")