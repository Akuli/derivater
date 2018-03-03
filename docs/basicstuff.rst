Basic Stuff
===========

.. currentmodule:: derivater

This page lists all functions that you'll likely end up using.


Symbols
-------

.. autoclass:: Symbol
.. autoclass:: SymbolFunction


The mathify function
--------------------

Derivater represents everything as instances of subclasses of
:class:`MathObjects <MathObject>`.

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

Every time we did ``2*x``, derivater converted the ``2`` into
``derivater.Integer(2)``. It looks a lot like a Python int, but it's not; it
has additional methods that derivater needs:

>>> Integer(2).derivative(x)
False
>>> 2 .derivative(x)
Traceback (most recent call last):
  ...
AttributeError: 'int' object has no attribute 'derivative'

.. autofunction:: mathify


Constants
---------

.. data:: e

    Euler's number, approximately 2.718281828459045.

.. data:: tau

    A full turn in radians, approximately 6.283185307179586.

.. data:: pi

    A convenient way to write ``tau/2``.


add, mul and pow
----------------

Usually it's easiest to do e.g. ``a + b`` instead of ``derivater.add(a, b)``,
but these functions can be faster if you want to e.g. add together a long list
of things. Using ``+``, ``-``, ``*``, ``/`` and ``**`` operators with
:class:`MathObjects <MathObject>` just calls these functions.

.. autofunction:: add
.. autofunction:: mul
.. autofunction:: pow
