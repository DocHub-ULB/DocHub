import sys
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "www.settings")
django.setup()


from django.core import serializers
import json
import os

from www.settings import BASE_DIR

from users.models import User

users = json.loads(serializers.serialize("json", User.objects.all(), fields=(
    'netid',
    'created',
    'first_name',
    'last_name',
    'email',
    'registration',
    'photo',
    'welcome',
    'comment',
    'is_staff',
    'is_academic',
    'is_representative',
)))

for user in users:
    user['fields']['edited'] = user['fields']['created']

users = json.dumps(users)

open(os.path.join(BASE_DIR, 'dumper', 'users.json'), 'w').write(users)


from graph.models import Course

courses = json.loads(serializers.serialize("json", Course.objects.all(), fields=(
    'slug', 'description',
)))

for course in courses:
    db_course = Course.objects.get(pk=course['pk'])
    course['fields']['name'] = db_course.name
    course['model'] = 'catalog.course'

courses = json.dumps(courses)

open(os.path.join(BASE_DIR, 'dumper', 'courses.json'), 'w').write(courses)

user_following_course = {}
for user in User.objects.all():
    slug_list = list(map(lambda x: x.slug, user.followed_courses()))
    user_following_course[user.netid] = slug_list

user_following_course = json.dumps(user_following_course)

open(os.path.join(BASE_DIR, 'dumper', 'user_following_course.json'), 'w').write(user_following_course)


from documents.models import Document, Page

documents = json.loads(serializers.serialize("json", Document.objects.all(), fields=(
    'description',
    'size',
    'pages',
    'date', # should be renamed to created
    'views',
    'downloads',
    'file_type',
    'original',
    'pdf',
    'state',
    'md5',
    'user', # swap user.pk to user.netid
)))

for document in documents:
    db_doc = Document.objects.get(pk=document['pk'])
    document['fields']['user'] = db_doc.user.netid
    document['fields']['created'] = document['fields']['date']
    document['fields']['edited'] = document['fields']['date']
    document['fields']['course'] = db_doc.parent.slug
    document['fields']['name'] = db_doc.name
    document['fields']['tags'] = list(map(lambda x: x.name, db_doc.keywords.all()))


documents = json.dumps(documents)
open(os.path.join(BASE_DIR, 'dumper', 'documents.json'), 'w').write(documents)


pages = serializers.serialize("json", Page.objects.all())
open(os.path.join(BASE_DIR, 'dumper', 'pages.json'), 'w').write(pages)


from telepathy.models import Thread, Message

threads = json.loads(serializers.serialize("json", Thread.objects.all(), fields=(
    'created', 'placement',
)))

for thread in threads:
    db_thread = Thread.objects.get(pk=thread['pk'])
    thread['fields']['user'] = db_thread.user.netid
    thread['fields']['name'] = db_thread.name
    thread['fields']['edited'] = thread['fields']['created']
    thread['fields']['user'] = db_thread.user.netid

    if isinstance(db_thread.parent, Document):
        thread['fields']['course'] = db_thread.parent.parent.slug
        thread['fields']['document'] = db_thread.parent.id
    else:
        thread['fields']['course'] = db_thread.parent.slug
        thread['fields']['document'] = None

threads = json.dumps(threads)
open(os.path.join(BASE_DIR, 'dumper', 'threads.json'), 'w').write(threads)


messages = json.loads(serializers.serialize("json", Message.objects.all(), fields=(
    'thread', 'text', 'created'
)))

for message in messages:
    db_message = Message.objects.get(pk=message['pk'])
    message['fields']['user'] = db_message.user.netid
    message['fields']['edited'] = message['fields']['created']

messages = json.dumps(messages)
open(os.path.join(BASE_DIR, 'dumper', 'messages.json'), 'w').write(messages)
