Basic Stuff
===========

.. currentmodule:: derivater

This page lists all functions that you'll likely end up using.


Symbols
-------

.. autoclass:: Symbol
.. autoclass:: SymbolFunction


MathObjects and Python objects
------------------------------

Derivater represents everything as instances of subclasses of MathObjects.

>>> x = Symbol('x')
>>> x
x
>>> type(x)
<class 'derivater._base.Symbol'>
>>> issubclass(Symbol, MathObject)
True
>>> type(2*x)
<class 'derivater._base.Mul'>
>>> issubclass(Mul, MathObject)
True

Note that I said *everything*; even integers are :class:`derivater.Integer`
objects and not Python ints:

>>> (2*x).objects
[2, x]
>>> (2*x).objects[0]
2
>>> type((2*x).objects[0])
<class 'derivater._base.Integer'>
>>> Integer(2)
2
>>> type(Integer(2))
<class 'derivater._base.Integer'>
>>> 2
2
>>> type(2)
<class 'int'>

When we did ``2*x``, derivater converted the ``2`` into
``derivater.Integer(2)``. It looks a lot like a Python int, but it's not; it
has additional methods that derivater needs:

>>> Integer(2).derivative(x)
0
>>> 2 .derivative(x)
Traceback (most recent call last):
  ...
AttributeError: 'int' object has no attribute 'derivative'

.. note::
    All derivater classes have all methods that MathObject has, so if there's
    some documentation for ``MathObject.toot()``, you can do e.g. ``x.toot()``,
    ``(2*x).toot()`` or ``ln(2).toot()``.

    There's a list of MathObject methods :ref:`below <mathobject-methods>`.

.. autofunction:: mathify

.. warning::
    Don't mutate math objects even if they use a mutable data structure like a
    list. Make a new, slightly different math object instead.


Simplifying
-----------

MathObjects provide two ways to simplify stuff:

.. automethod:: MathObject.gentle_simplify
.. automethod:: MathObject.simplify


.. _mathobject-methods:

More MathObject Methods
-----------------------

Some of this documentation talks about *overriding*. You can ignore all that if
you don't know what overriding is. However, if you are implementing a custom
MathObject subclass and you are  are interested in the overriding stuff, also
check out :ref:`this customizing guide <custom>`.

.. automethod:: MathObject.derivative
.. automethod:: MathObject.may_depend_on
.. automethod:: MathObject.replace

.. automethod:: MathObject.apply_to_content
.. automethod:: MathObject.apply_recursively
.. automethod:: MathObject.get_content
