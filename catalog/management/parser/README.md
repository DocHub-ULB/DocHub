# ULB Parser

To parse all the courses from the ULB (as of august 2021)
```bash
python3 parse_courses.py
python3 build_tree.py
# (From the root of the repo)
./manage.py shell < catalog/management/parser/load_courses.py
```
