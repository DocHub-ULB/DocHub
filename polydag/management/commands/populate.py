from polydag.models import Node, Taggable, Leaf
from django.core.management.base import BaseCommand

# To bring new colors to the graph, simply:
#   from graph.management.commands.graphviz import Command
#   Command.COLORS['MyNewType'] = 'purple'
# note: color list is available at http://www.graphviz.org/content/color-names

class Command(BaseCommand):
    def mkNode(self, name):
        return Node.objects.create(name=name)


    def mkTaggable(self, name, *tags):
        res = Taggable.objects.create(name=name)
        res.add_keywords(tags)
        return res


    def mkLeaf(self, name):
        return Leaf.objects.create(name=name)

    def handle(self, *args, **options):
        root = self.mkNode("P402 - Whiteboard")

        info = self.mkNode("Sciences Informatiques")
        root.add_child(info)

        ba1info = self.mkNode("BA1 Sciences Informatiques")
        info.add_child(ba1info)
        progra = self.mkNode("INFO-F-101")
        ba1info.add_child(progra)
        progra.add_child(self.mkLeaf("Question projet 1"))

        ba1info.add_child(self.mkNode("INFO-F-102"))
        ba1info.add_child(self.mkNode("INFO-F-103"))
        ba1info.add_child(self.mkNode("INFO-F-105"))
        ba1info.add_child(self.mkNode("INFO-F-106"))
        ba1info.add_child(self.mkNode("MATH-F-107"))
        ba1info.add_child(self.mkNode("PHYS-F-103"))

        options = self.mkNode("Options")
        ba1info.add_child(options)
        options.add_child(self.mkNode("MATH-F-110"))
        options.add_child(self.mkNode("MATH-F-111"))

        math = self.mkNode("Sciences mathematiques")
        root.add_child(math)
        ba1math = self.mkNode("BA1 Sciences mathematiques")
        math.add_child(ba1math)
        ba1math.add_child(options)