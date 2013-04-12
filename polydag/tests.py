"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from polydag.models import Node, Leaf, Taggable, TaggableLeaf, CannotHaveChildren

class SimpleTest(TestCase):
    def mkNode(self, name, klass=Node):
        """Helper function to easily create nodes or inherited"""
        return klass.objects.create(name=name)
    
    
    def testAttach(self):
        """
        A -> B -> C -> D
        A -> D
        A -> E -> B
        """
        a, b, c, d, e = (self.mkNode(chr(ord('A')+i)) for i in range(5))
        ### AdventureTime !
        self.assertTrue(a.attach(b) and b.attach(c) and c.attach(d), 'Construct basic graph')
        self.assertTrue(a.attach(d), 'Another path')
        self.assertTrue(a.attach(e), 'Attach single new node')
        self.assertTrue(e.attach(b), 'Insert reference from new node')
        self.assertFalse(d.attach(a), 'Direct loop')
        self.assertFalse(c.attach(e), 'Indirect loop')
        self.assertTrue(c.attach(e, False), 'Force attach with loop')
    
    
    def testLeaves(self):
        leaf = self.mkNode("Leaf", Leaf)
        node = self.mkNode("Node")
        self.assertRaises(CannotHaveChildren, leaf.attach, node, msg='Leaf cannot have child')
    
    
    def testReachablility(self):
        """
        Test some reachability methods on a simple graph
        A -> B -> E
        A -> C -> D
        C -> E
        """
        a, b, c, d, e = (self.mkNode(chr(ord('A')+i)) for i in range(5))
        a.attach(b) and b.attach(e)
        a.attach(c) and c.attach(d)
        c.attach(e)
        walktypes = {'depth_first':True, 'breadth_first':False}
        ### AdventureTime !
        for walk in walktypes:
            depth_first = walktypes[walk]
            walk = '('+walk+')'
            self.assertTrue(e.has_ancestor(c, depth_first), 'Direct parent->child relation '+walk)
            self.assertTrue(e.has_ancestor(b, depth_first), 'Direct parent->child relation (alt) '+walk)
            self.assertTrue(e.has_ancestor(a, depth_first), 'Grandfather->grandchild relation '+walk)
            self.assertFalse(d.has_ancestor(b, depth_first), 'No relation '+walk)
    
    
    def testTaggableLeaf(self):
        root = self.mkNode("Root")
        a, b, c = (self.mkNode(chr(ord('A')+i), TaggableLeaf) for i in range(3))
        a.add_keywords('pig', 'a')
        b.add_keywords('pig', 'b')
        c.add_keywords('c')
        child = self.mkNode("child")
        root.attach(a) and root.attach(b) and root.attach(c)
        ### AdventureTime !
        self.assertIn(b, a.related(), 'Basic tag-based relation')
        self.assertNotIn(c, a.related(), 'Basic tag-based no-relation')
        self.assertRaises(CannotHaveChildren, a.attach, child, msg='Leaf cannot have child')
    
    
    def testRelated(self):
        avl = self.mkNode('AVL', Taggable)
        avl.add_keywords('bst', 'tree', 'balanced')
        splice = self.mkNode('Splice game', Taggable)
        splice.add_keywords('tree', 'game')
        poney = self.mkNode('My Little Poney', Taggable)
        poney.add_keywords('poney', 'Bram', 'bot', 'irc')
        ### AdventureTime !
        self.assertIn(splice, avl.related(), 'Basic tag-based relation')
        self.assertNotIn(poney, avl.related(), 'Basic tag-based no-relation')
    
