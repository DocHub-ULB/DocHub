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

from django.test import TestCase
from polydag.models import Node, CycleError


class SimpleTest(TestCase):
    def testAttach(self):
        #parent -> child1 -> child2
        #   |-------------------^
        parent = Node.objects.create(name="root")
        child1 = Node.objects.create(name="child1")
        child2 = Node.objects.create(name="child2")
        self.assertTrue(parent.add_child(child1))
        self.assertTrue(child2.add_parent(parent))
        self.assertTrue(child1.add_child(child2))
        self.assertRaises(CycleError, child2.add_child, (child1))

        self.assertIn(child1, parent.children())
        self.assertIn(parent, child1.parents())

        self.assertIn(child2, parent.children())
        self.assertIn(parent, child2.parents())

        self.assertIn(child2, child1.children())
        self.assertIn(child1, child2.parents())

        self.assertNotIn(child1, child2.children())
        self.assertNotIn(child2, child1.parents())


    def testClassBasename(self):
        self.assertEqual('Node', Node().classBasename())
        class Carapils(Node):
            pass
        self.assertEqual('Carapils', Carapils().classBasename())


    def testSets(self):
        GRANDfather = Node.objects.create(name="grand-grandfather")
        grandfather = Node.objects.create(name="grandfather")
        father = Node.objects.create(name="father")
        son = Node.objects.create(name="son")
        grandson = Node.objects.create(name="grandson")

        GRANDfather.add_child(grandfather)
        grandfather.add_child(father)
        father.add_child(son)
        son.add_child(grandson)

        descendants = grandfather.descendants_set()
        self.assertNotIn(GRANDfather, descendants)
        self.assertNotIn(grandfather, descendants)
        self.assertIn(father, descendants)
        self.assertIn(son, descendants)
        self.assertIn(grandson, descendants)

        ancestors = grandson.ancestors_set()
        self.assertNotIn(grandson, ancestors)
        self.assertIn(father, ancestors)
        self.assertIn(son, ancestors)
        self.assertIn(grandfather, ancestors)

