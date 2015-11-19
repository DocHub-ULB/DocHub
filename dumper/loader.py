import sys
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "www.settings")
django.setup()


from django.core import serializers
import os
import json

from www.settings import BASE_DIR


users = open(os.path.join(BASE_DIR, 'dumper', 'users.json'), 'r').read()

for user in serializers.deserialize("json", users):
    user.object.comment = ""
    user.save()


courses = open(os.path.join(BASE_DIR, 'dumper', 'courses.json'), 'r').read()

for course in serializers.deserialize("json", courses):
    course.save()


from users.models import User
from catalog.models import Course
from actstream import actions

user_following_course = json.loads(open(os.path.join(BASE_DIR, 'dumper', 'user_following_course.json'), 'r').read())

for user, followed_courses in user_following_course.items():
    user = User.objects.get(netid=user)
    courses = Course.objects.filter(slug__in=followed_courses)
    for course in courses:
        actions.follow(user, course, actor_only=False)


from tags.models import Tag

documents = json.loads(open(os.path.join(BASE_DIR, 'dumper', 'documents.json'), 'r').read())

for document in documents:
    course = Course.objects.get(slug=document['fields']['course'])
    document['fields']['course'] = course.id
    user = User.objects.get(netid=document['fields']['user'])
    document['fields']['user'] = user.id
    tags = document['fields']['tags']
    document['fields']['tags'] = []
    for tag in tags:
        obj, _ = Tag.objects.get_or_create(name=tag)
        document['fields']['tags'].append(obj.id)

documents = json.dumps(documents)

for document in serializers.deserialize("json", documents):
    document.save()


from documents.models import Page

pages = open(os.path.join(BASE_DIR, 'dumper', 'pages.json'), 'r').read()
pages = serializers.deserialize("json", pages)
pages = map(lambda x: x.object, pages)
pages = list(pages)

Page.objects.bulk_create(pages)


from users.models import User
from catalog.models import Course
from documents.models import Document

threads = json.loads(open(os.path.join(BASE_DIR, 'dumper', 'threads.json'), 'r').read())

for thread in threads:
    if thread['fields']['document'] is not None:
        document = Document.objects.get(id=thread['fields']['document'])
        thread['fields']['document'] = document.id

    user = User.objects.get(netid=thread['fields']['user'])
    thread['fields']['user'] = user.id

    course = Course.objects.get(slug=thread['fields']['course'])
    thread['fields']['course'] = course.id
    if thread['fields']['placement'] is None:
        thread['fields']['placement'] = ""

threads = json.dumps(threads)

for thread in serializers.deserialize("json", threads):
    thread.save()
