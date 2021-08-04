# ULB Parser

To parse all the courses from the ULB (as of august 2021)
```bash
# (From the root of the repo)
python3 catalog/management/parser/parse_courses.py
python3 catalog/management/parser/build_tree.py
./manage.py shell < catalog/management/parser/load_courses.py
```
