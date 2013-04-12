from polydag.models import Node
from django.core.management.base import BaseCommand
from optparse import make_option

# To bring new colors to the graph, simply:
#   from graph.management.commands.graphviz import Command
#   Command.COLORS['MyNewType'] = 'purple'
# note: color list is available at http://www.graphviz.org/content/color-names

class Command(BaseCommand):
    COLORS = {
        'Node' : 'grey',
        'Leaf': 'lightblue',
        'Taggable': 'coral'
    }

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
        for node in Node.objects.all():
            color = self.COLORS.get(node.classBasename(), self.COLORS['Node'])
            url = options['urlprefix'] + node.canonic_url
            f.write('\t%d [style=filled label="%s" fillcolor=%s URL="%s"]\n'%(node.pk, str(node.name), color, url))
            for child in node.childrens():
                f.write('\t%d -> %d;\n'%(node.pk, child.id))

        #Color legend
        f.write('edge [style=invis];\n')
        for className in self.COLORS:
            f.write('\t"%s" [style=filled,fillcolor=%s,shape=box,margin="0,0",width=1,height=0.5,arrow=none]'%(className, self.COLORS[className]))
        i = 0
        for className in self.COLORS:
            if i>0: f.write(' -> ')
            f.write('"'+className+'"')
            i += 1
        f.write('}\n')