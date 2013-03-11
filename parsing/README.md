Instructions
============

À exécuter dans cet ordre:

* mkdir catalogs
* mkdir cours
* python dl.py
* python parse_catalogs_n_dl_courses.py
* python parse_cours.py

Si un script plante à cause d'un timeout, le relancer, normalement il redlera pas les fichiers déjà fait (par contre ça peut créer un fichier vide (j'ai édité les fichiers sans tester (les to_write), il se peut que ça plante à ces endroits là)).

Remarque importante
===================

J'ai tapé un exemple de données dans example.json

IL VA PROBABLEMENT MANQUER DES INFORMATIONS QUI NE SONT PAS DANS LES PAGES QUE J'AI PARSÉ. Là je transforme ces pages là http://banssbfr.ulb.ac.be/PROD_frFR/bzscrse.p_disp_course_detail?cat_term_in=201213&subj_code_in=COMM&crse_numb_in=P100&PPAGE=ESC_PROGCAT_AREREQ&PPROGCODE=BA-ARCH&PAREA=ARCH1&PARETERM=201112&PTERM=201213 en json, je suis quasi sûr qu'il n'y aura pas assez d'informations dedans, il faudra probablement les extraires dans le script parse_catalogs_n_dl_courses.py

Hast modif
==========
Pour generer une initial_data pour peupler la DB, editer tree.json (structure des cat/subcat/course du nouveau site) puis executer
* python generate.py > ../initial_data.json

