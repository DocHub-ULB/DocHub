# How to generate a new tree at the beginning of the year ?

## Download up to data data from ULB
Run 
```shell
./manage.py download_programs
./manage.py download_program_contents
```
It will generate `programs.json` and `courses.json` at
the root containing what is required to build the new tree.

## Find and fix orphans
1. run `./manage.py find_orphans` that will dump a list of courses having 
   documents that are not in the new course list
2. run `./manage.py crawl_uv` to get a list of all courses (from every year)
3. TODO: add here a script that detects orphans
4. TODO: add here a script that moves the orphans to their new slugs (and leaves a redirect behind)

## Insert the new data in the DB

1. run `./manage.py load_tree` that will delete all categories and replace them with the new ones
2. run `./manage.py load_courses` that will create missing courses + assign categories to all courses
   (and will not touch orphan courses) 

