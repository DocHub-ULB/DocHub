# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2013, iTitou. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This module contains variants to include in polydag.models classes to add
# some custom behaviors (no children, single parent, ...)

class CannotHaveChildren(Exception):
    """Exception raised by graph nodes that doesn't accept children"""
    def __init__(self, node):
        msg = node.classBasename()+'#'+str(node.pk)+' can\'t have children'
        Exception.__init__(self, msg)



class CannotHaveManyParents(Exception):
    """Exception raised by graph nodes that doesn't accept more than 1 parent"""
    def __init__(self, node):
        msg = node.classBasename()+'#'+str(node.pk)+' can\'t have more than 1 parent'
        Exception.__init__(self, msg)



class Leaf:
    """Simple mixin that brings a Leaf behavior to a Node"""
    def children(self):
        """Since self cannot have children, bypass DB lookup !"""
        return []


    def add_child(self, *args, **kwargs):
        raise CannotHaveChildren(self)



class OneParent:
    @property
    def parent(self):
        parents = self.parents()
        if len(parents) > 0:
            return parents[0]
        else:
            return None


    def pre_attach_hook(self):
        if len(self.parents()) > 0:
            raise CannotHaveManyParents(self)


    def move(self,newparent):
        """Move a OneParentNode from his current parent to newparent"""
        oldparent = self.parent
        if oldparent:
            self.detatch_from(oldparent)
        newparent.add_child(self)

