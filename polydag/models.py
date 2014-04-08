# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# POLYmorphic Directed Acyclic Graph

from django.db import models
import re
from database import grapheek
from django.db.models.signals import post_save
from polymorphic import PolymorphicModel


def to_django(nodes):
    ids = set()
    for node in nodes:
        d = node.data()
        ids.add(d['id'])
    return Node.objects.filter(id__in=list(ids))


class Node(PolymorphicModel):
    """Base class for all P402 objects"""
    name = models.CharField(max_length=140)

    @property
    def __basename__(self):
        """Return the class name without modules prefix"""
        klass = str(type(self))  # "<class 'foo.bar'>"
        return re.sub(r'.*[\.\']([^\.]+)\'>$', r'\1', klass)

    def graph_node(self):
        with grapheek() as g:
            node = g.V(id=self.pk)
        node = list(node)
        if len(node) < 1:
            if self.pk is None:
                raise UnsavedModel("'{}' was not saved in the db".format(self))
            else:
                raise GraphInconsistency(
                    "Object of type {} and pk {} was not found in the graph, this is BAD !".format(
                        self.__basename__, self.pk)
                )
        elif len(node) > 1:
            raise GraphInconsistency(
                "Object of type '{}' and pk {} was found more than once ({} times) in the graph, this is BAD !".format(
                    self.__basename__, self.pk, len(node))
            )
        return node[0]

    def children(self):
        return self.graph_node().outV()

    def parents(self):
        return self.graph_node().inV()

    # def descendants(self):
    #     l = []

    #     def getchildren(start_node, l):
    #         t = list(start_node.outV())
    #         l += t
    #         for node in t:
    #             getchildren(node, l)
    #     getchildren(self.graph_node(), l)
    #     return l

    # def ancestors(self):
    #     l = []

    #     def getparents(start_node, l):
    #         t = list(start_node.inV())
    #         l += t
    #         for node in t:
    #             getparents(node, l)
    #     getparents(self.graph_node(), l)
    #     return l

    def descendants(self):
        total = []
        current_level = None
        current_query = self.graph_node()
        while current_level != []:
            current_query = current_query.outV()
            current_level = list(current_query)
            total += current_level
        return total

    def ancestors(self):
        total = []
        current_level = None
        current_query = self.graph_node()
        while current_level != []:
            current_query = current_query.inV()
            current_level = list(current_query)
            total += current_level
        return total

    def add_child(self, child, acyclic_check=True):
        """
        Attach a new child to self. If acyclic_check evaluates
        to True, and a loop occurs with this new edge, don't add the new child
        and raise CycleError.
        """
        child.pre_attach_hook()
        if acyclic_check and child.hasCycle([self]):
            raise CycleError
        with grapheek() as g:
            g.add_edge(self.graph_node(), child.graph_node())

    def add_parent(self, parent):
        """Add a parent to self"""
        return parent.add_child(self)

    def pre_attach_hook(self):
        pass

    def remove_child(self, child):
        outEdges = self.graph_node().outE()
        for edge in outEdges:
            if edge.outV().data() == child.graph_node().data():
                edge.remove()

    def remove_parent(self, parent):
        parent.remove_child(self)

    def hasCycle(self, traversed):
        """Recursively walk the graph to find any loop"""
        res = False
        if self in traversed:
            res = True
        else:
            traversed.append(self)
            for child in self.children():
                if child.hasCycle(traversed):
                    res = True
                    break
            traversed.pop()
        return res

    def to_dict(self, with_children=False):
        res = {
            'id': self.pk, 'name': self.name,
            'type': self.__basename__
        }
        #res['url'] = self.canonic_url
        if with_children:
            res['children'] = []
            for child in to_django(self.children()):
                res['children'].append(child.to_dict(False))
        return res

    def is_reachable_from(self, ancestor, depth_first=True):
        """Return True if self could be reached from ancestor"""
        for parent in self.ancestors():
            if parent == ancestor or (depth_first and parent.is_reachable_from(ancestor)):
                return True
        if not depth_first:
            for parent in self.ancestors():
                if parent.is_reachable_from(ancestor):
                    return True
        return False


class Keyword(models.Model):
    """
    Keywords are a comfortable way to group object that are far from each other
    in the site's graph, but semantically close.
    """
    name = models.CharField(max_length=50)


class Taggable(Node):
    """An abstract taggable node. Taggable nodes have keywords."""
    keywords = models.ManyToManyField(Keyword)

    @staticmethod
    def KW(name):
        """Simply create or get a keyword"""
        #Keywords are always lowercased
        existing, created = Keyword.objects.get_or_create(name=name.lower())
        return existing if existing else created

    def add_keywords(self, *tags):
        """Add a keyword by directly passing its name"""
        for tag in tags:
            self.keywords.add(self.KW(tag))

    def related_list(self):
        """
        Return a list of taggable objects that share some keywords with self.
        """
        res = []
        for kw in self.keywords.all():
            for node in kw.taggable_set.all():
                if node in res:
                    res.remove(node)
                    res.insert(0, node)
                else:
                    res.append(node)
        return res

    related = related_list


def node_save_callback(sender, created, instance, **kwargs):
    if not isinstance(instance, Node) or not created:
        return None
    with grapheek() as g:
        g.add_node(id=instance.pk, label=instance.__basename__)

post_save.connect(node_save_callback)


class CycleError(StandardError):
    pass


class GraphInconsistency(StandardError):
    pass


class UnsavedModel(StandardError):
    pass
