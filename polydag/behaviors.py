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


class CannotHaveChildren(Exception):
    """Exception raised by graph nodes that doesn't accept children"""
    def __init__(self, node):
        msg = node.__basename__ + '#' + str(node.pk) + ' can\'t have children'
        Exception.__init__(self, msg)


class CannotHaveManyParents(Exception):
    """Exception raised by graph nodes that doesn't accept more than 1 parent"""
    def __init__(self, node):
        msg = node.__basename__ + '#' + str(node.pk) + ' can\'t have more than 1 parent'
        Exception.__init__(self, msg)


class Leaf:
    """Simple mixin that brings a Leaf behavior to a Node"""
    def children(self, *args, **kwargs):
        """Since self cannot have children, bypass DB lookup !"""
        return []

    def add_child(self, *args, **kwargs):
        raise CannotHaveChildren(self)


class OneParent:
    @property
    def parent(self, *args, **kwargs):
        parents = self.parents()
        if parents.count() > 0:
            return list(parents.limit(1))[0]
        else:
            return None

    def pre_attach_hook(self, *args, **kwargs):
        if self.parents().count() > 0:
            raise CannotHaveManyParents(self)

    def move(self, newparent, *args, **kwargs):
        """Move a OneParentNode from his current parent to newparent"""
        oldparent = self.parent
        if oldparent:
            self.detatch_from(oldparent)
        newparent.add_child(self)
