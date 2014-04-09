# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from polydag.models import Node
from django.core.management.base import BaseCommand
from optparse import make_option
from django.db.models import Q

# To bring new colors to the graph, simply:
#   from graph.management.commands.graphviz import Command
#   Command.COLORS['MyNewType'] = 'purple'
# note: color list is available at http://www.graphviz.org/content/color-names


class Command(BaseCommand):
    COLORS = {
        'Node': 'grey',
        'Leaf': 'lightblue',
        'Taggable': 'coral'
    }

    EXCLUDE = []

    help = """
    Export the main graph to graphviz format
    see also: http://www.graphviz.org/Documentation.php
    Use in combination with dot (or circo, neato, twopi, ...)
    manage.py graphviz | dot -Tpng > graph.png
    """

    option_list = BaseCommand.option_list + (
        make_option('-u', '--urlprefix',
                    action='store',
                    dest='urlprefix',
                    default="http://localhost:8000",
                    help='URL prefix for clickable nodes'
                    ),
    )

    def handle(self, *args, **options):
        f = self.stdout
        f.write('digraph P402 {\n')
        excludes_q = map(lambda x: Q(not_instance_of=x), self.EXCLUDE)
        query = Node.objects.all()
        if len(excludes_q) > 0:
            query = query.filter(*excludes_q)
        for node in query:
            color = self.COLORS.get(node.__basename__, self.COLORS['Node'])
            url = options['urlprefix']  # + node.canonic_url
            f.write('\t%d [style=filled label="%s" fillcolor=%s URL="%s"]\n' % (node.pk, node.name, color, url))
            for child in node.children(exclude=self.EXCLUDE):
                f.write('\t%d -> %d;\n' % (node.pk, child.id))

        #Color legend
        f.write('edge [style=invis];\n')
        for className in self.COLORS:
            f.write('\t"%s" [style=filled,fillcolor=%s,shape=box,margin="0,0",width=1,height=0.5,arrow=none]' % (className, self.COLORS[className]))
        i = 0
        for className in self.COLORS:
            if i > 0:
                f.write(' -> ')
            f.write('"' + className + '"')
            i += 1
        f.write('}\n')
