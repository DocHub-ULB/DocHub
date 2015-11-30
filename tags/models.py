from django.db import models
from math import sin, pi


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    @property
    def color(self):
        return "#%02x%02x%02x" % tuple(
            abs(int(200 * sin(self.id + x * pi / 3))) for x in range(3))

    def __unicode__(self):
        return self.name
