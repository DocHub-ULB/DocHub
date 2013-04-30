# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from json import loads
from polydag.models import Node
from django.db import models
from users.models import Profile
from documents.models import Document
from telepathy.models import Message, Thread

class Course(Node):
    slug = models.SlugField()
    description = models.TextField(null=True)
    
    @property
    def last_activity(self):
        last_act = []
        last_docs = self.children().instance_of(Document).order_by('-Document___date')[:1]
        if len(last_docs) == 1:
            last_act.append(last_docs[0].date)
        
        threads = self.children().instance_of(Thread)
        last_msgs = Message.objects.filter(thread__in=threads).order_by('-created')[:1]
        if len(last_msgs) == 1:
            last_act.append(last_msgs[0].created)
        return max(last_act) if len(last_act)>0 else "NA"
    
    
    def last_info(self):
        dataset = self.courseinfo_set.all()
        data = dataset[0] if len(dataset)>0 else CourseInfo(infos="[]")
        data.infos = loads(data.infos)
        return data
    


class CourseInfo(models.Model):
    user = models.ForeignKey(Profile)
    infos = models.TextField()
    date = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course)
    
    class Meta:
        ordering = ['-date']
    


class Category(Node):
    slug = models.SlugField()
    description = models.TextField(null=True)

