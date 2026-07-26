from math import pi, sin

from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    @property
    def color(self):
        r, g, b = (abs(int(200 * sin(self.id + x * pi / 3))) for x in range(3))
        return f"#{r:02x}{g:02x}{b:02x}"

    def __str__(self):
        return self.name
