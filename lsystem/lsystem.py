# -*- coding: utf-8 -*-
"""
A simple l-system
"""
from math import radians
from random import random, seed
from collections import namedtuple
from mathutils import Vector, Matrix


Quad = namedtuple('Quad', 'pos, up, right, forward')
Edge = namedtuple('Edge', 'start, end, radius')
BObject = namedtuple('BObject', 'name, pos, up, right, forward')


class Turtle(object):

    def __init__(self,
                 tropism=(0, 0, 0),
                 tropismsize=0,
                 pitch_angle=radians(30),
                 yaw_angle=radians(30),
                 roll_angle=radians(30),
                 radius=0.2,
                 iseed=42):
        self.tropism = Vector(tropism).normalized()
        self.magnitude = tropismsize
        self.forward = Vector((1, 0, 0))
        self.up = Vector((0, 0, 1))
        self.right = self.forward.cross(self.up)
        self.stack = []
        self.stack_curly = []
        self.position = Vector((0, 0, 0))
        self.pitch_angle = pitch_angle
        self.yaw_angle = yaw_angle
        self.roll_angle = roll_angle
        self.radius = radius
        self.__init_terminals()
        seed(iseed)

    def __init_terminals(self):
        """
        Initialize a map of predefined terminals.
        """
        self.terminals = {
            '+': self.term_plus,
            '-': self.term_minus,
            '[': self.term_push,
            ']': self.term_pop,
            '(': self.term_push_curly,
            ')': self.term_pop_curly,
            '/': self.term_slash,
            '\\': self.term_backslash,
            '<': self.term_less,
            '>': self.term_greater,
            '&': self.term_amp,
            '!': self.term_expand,
            '@': self.term_shrink,
            '#': self.term_fatten,
            '%': self.term_slink,
            '^': self.term_expand_g,
            '*': self.term_shrink_g,
            '=': self.term_fatten_g,
            '|': self.term_slink_g,
            'F': self.term_edge,
            'Q': self.term_quad,
            # '{': self.term_object
            }

    def apply_tropism(self):
        # tropism is a normalized vector
        t = self.tropism * self.magnitude
        tf = self.forward + t
        tf.normalize()
        q = tf.rotation_difference(self.forward)
        self.forward.rotate(q)
        self.up.rotate(q)
        self.right.rotate(q)

    def term_plus(self, value=None):
        val = radians(value) if not value is None else self.pitch_angle
        r = Matrix.Rotation(val, 4, self.right)
        self.forward.rotate(r)
        self.up.rotate(r)

    def term_minus(self, value=None):
        val = radians(value) if not value is None else self.pitch_angle
        r = Matrix.Rotation(-val, 4, self.right)
        self.forward.rotate(r)
        self.up.rotate(r)

    def term_amp(self, value=30):
        k = (random() - 0.5) * value
        self.term_plus(value=k)
        k = (random() - 0.5) * value
        self.term_slash(value=k)

    def term_slash(self, value=None):
        r = Matrix.Rotation(radians(value) if not value is None
                            else self.yaw_angle, 4, self.up)
        self.forward.rotate(r)
        self.right.rotate(r)

    def term_backslash(self, value=None):
        r = Matrix.Rotation(-radians(value) if not value is None
                            else -self.yaw_angle, 4, self.up)
        self.forward.rotate(r)
        self.right.rotate(r)

    def term_less(self, value=None):
        r = Matrix.Rotation(radians(value) if not value is None
                            else self.roll_angle, 4, self.forward)
        self.up.rotate(r)
        self.right.rotate(r)

    def term_greater(self, value=None):
        r = Matrix.Rotation(-radians(value) if not value is None
                            else -self.roll_angle, 4, self.forward)
        self.up.rotate(r)
        self.right.rotate(r)

    def term_pop(self, value=None):
        t = self.stack.pop()
        (self.forward,
         self.up,
         self.right,
         self.position,
         self.radius) = t

    def term_push(self, value=None):
        t = (self.forward.copy(),
             self.up.copy(),
             self.right.copy(),
             self.position.copy(),
             self.radius)
        self.stack.append(t)

    def term_pop_curly(self, value=None):
        t = self.stack_curly.pop()
        (self.forward,
         self.up,
         self.right,
         self.position,
         self.radius) = t

    def term_push_curly(self, value=None):
        t = (elf.forward.copy(),
             elf.up.copy(),
             elf.right.copy(),
             elf.position.copy(),
             elf.radius)
        self.stack_curly.append(t)

    expand_shrink_factor = 0.1
    fatten_slink_factor = 0.045
    expand_shrink_factor_g = 0.2
    fatten_slink_factor_g = 0.48

    def term_expand(self, value=1 + expand_shrink_factor):
        self.forward *= value
        self.up *= value
        self.right *= value

    def term_shrink(self, value=1 - expand_shrink_factor):
        self.forward *= value
        self.up *= value
        self.right *= value

    def term_fatten(self, value=1 + fatten_slink_factor):
        self.radius *= value

    def term_slink(self, value=1 - fatten_slink_factor):
        self.radius *= value

    def term_expand_g(self, value=1 + expand_shrink_factor_g):
        self.term_expand(1 + 0.48)

    def term_shrink_g(self, value=1 - expand_shrink_factor_g):
        self.term_shrink(value)

    def term_fatten_g(self, value=1 + fatten_slink_factor_g):
        self.term_fatten(value)

    def term_slink_g(self, value=1 - fatten_slink_factor_g):
        self.term_slink(value)

    def term_edge(self, value=None):
        s = self.position.copy()
        self.apply_tropism()
        self.position += self.forward
        e = self.position.copy()
        return Edge(start=s, end=e, radius=self.radius)

    def term_quad(self, value=0.5):
        return Quad(pos=self.position,
                    right=self.right,
                    up=self.up,
                    forward=self.forward)

    def term_object(self, value=None, name=None):
        s = self.position.copy()
        self.apply_tropism()
        self.position += self.forward
        return BObject(name=name,
                       pos=s,
                       right=self.right,
                       up=self.up,
                       forward=self.forward)

    def interpret(self, s):
        """
        interpret the iterable s, yield Quad, Edge or Object named tuples.
        """
        print('interpret:', s)
        name = ''
        for c in s:
            t = None
            #print(c,name)
            if c == '}':
                t = self.term_object(name=name[1:])
                name = ''
            elif c == '{' or name != '':
                name += c
                continue
            elif name != '':
                continue
            elif c in self.terminals:
                t = self.terminals[c]()
            #print('yield',t)
            if not t is None:
                yield t
