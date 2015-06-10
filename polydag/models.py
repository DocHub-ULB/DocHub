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

'''POLYmorphic Directed Acyclic Graph'''

from django.db import models
from polymorphic import PolymorphicModel
from math import sin, pi
import re


class Node(PolymorphicModel):
    """Base class for all P402 objects"""
    name = models.CharField(max_length=140, db_index=True)
    _children = models.ManyToManyField("self", symmetrical=False, blank=True, db_index=True)

    def __unicode__(self):
        return "Node ({}) #{}: {}".format(self.classBasename(), self.id, self.name)

    def children(self, only=[], exclude=[], id_only=False):
        """Return a list of all self's direct children"""
        only_q = map(lambda x: models.Q(instance_of=x), only)
        exclude_q = map(lambda x: models.Q(not_instance_of=x), exclude)

        query = self._children.all()
        if len(only_q) > 0:
            query = query.filter(*only_q)
        elif len(exclude_q):
            query = query.filter(*exclude_q)

        if id_only:
            query = query.only('id').non_polymorphic()

        return query

    def parents(self):
        """Return a list of all self's direct parents"""
        return Node.objects.filter(_children=self)

    def descendants_tree(self, id_only=False):
        """
        Returns a tree of the node's  children by depth-first search
        """
        tree = {}
        for node in self.children(id_only=id_only):
            tree[node] = node.descendants_tree(id_only)
        return tree

    def descendants_set(self, id_only=False):
        """Returns a list of the node's  children by depth-first search"""
        tree = self.descendants_tree(id_only)
        return self.tree_to_set(tree)

    def ancestors_set(self):
        """Returns a list of the node's  children by depth-first search"""
        tree = self.ancestors_tree()
        return self.tree_to_set(tree)

    def tree_to_set(self, tree):
        track = set()
        for node in tree:
            if not tree[node] == {}:
                track.update(self.tree_to_set(tree[node]))
            track.add(node)
        return track

    def ancestors_tree(self):
        """Returns an ancestors tree"""
        tree = {}
        for node in self.parents():
            tree[node] = node.ancestors_tree()
        return tree

    def add_child(self, child, acyclic_check=True):
        """
        Attach a new child to self and return True. If acyclic_check evaluates
        to True, and a loop occurs with this new edge, don't add the new child
        and return False.
        """
        child.pre_attach_hook()
        if acyclic_check and child.hasCycle([self]):
            raise CycleError
        self._children.add(child)
        self.save()
        return True

    def add_parent(self, parent):
        """Add a parent to self"""
        return parent.add_child(self)

    def pre_attach_hook(self):
        pass

    def remove_parent(self, parent):
        """Detatch self from parent. Return none"""
        parent._children.remove(self)
        parent.save()

    def remove_child(self, child):
        """Remove child from self"""
        child.remove_parent(self)

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

    def classBasename(self):
        """Return the class name without modules prefix"""
        klass = str(type(self))  # "<class 'foo.bar'>"
        return re.sub(r'.*[\.\']([^\.]+)\'>$', r'\1', klass)

    def to_dict(self, with_children=False):
        res = {
            'id': self.pk, 'name': self.name,
            'type': self.classBasename()
        }
        # res['url'] = self.canonic_url
        if with_children:
            res['children'] = []
            for child in self.children():
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
    name = models.CharField(max_length=50, unique=True)

    @property
    def color(self):
        return "#%02x%02x%02x" % tuple(
            abs(int(200 * sin(self.id + x * pi / 3))) for x in range(3))

    def __unicode__(self):
        return self.name


class Taggable(Node):
    """An abstract taggable node. Taggable nodes have keywords."""
    keywords = models.ManyToManyField(Keyword, blank=True, db_index=True)
    year = models.CharField(max_length=9, db_index=True)

    @staticmethod
    def KW(name):
        """Simply create or get a keyword"""
        # Keywords are always lowercased
        if isinstance(name, Keyword):
            return name
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


class CycleError(StandardError):
    pass
