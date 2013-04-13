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
    def childrens(self):
        """Since self cannot have children, bypass DB lookup !"""
        return []
    
    
    def attach(self, *args, **kwargs):
        raise CannotHaveChildren(self)
    


class OneParent:
    """Simple mixin that allows for a node to ony have 1 parent"""
    def parent(self):
        return self.ancestors()[0]
    
    
    def pre_attach_hook(self):
        if len(self.ancestors()) > 0:
            raise CannotHaveManyParents(self)
    
