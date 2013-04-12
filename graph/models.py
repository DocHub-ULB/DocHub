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


class Course(Node):
    slug = models.SlugField()
    description = models.TextField(null=True)
    
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
    description = models.TextField(null=True)
    slug = models.SlugField()

