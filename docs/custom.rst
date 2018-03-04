.. _custom:

Custom Math Objects and Stuff
=============================

.. currentmodule:: derivater

If you just want to take derivatives of stuff you don't need anything
documented here, but this stuff lets you implement things like custom math
objects that work with derivater.


.. _log2-class-example:

Custom Math Object Example
--------------------------

Derivater doesn't have a class for base 2 logarithms by default and ``log2(x)``
just returns ``ln(x) / ln(2)``. Let's implement an actual base 2 logarithm
object to see how things go.
::

    from derivater import MathObject, Symbol, mathify


    class Base2Log(MathObject):

        def __init__(self, numerus):
            self.numerus = mathify(numerus)

        def __repr__(self):
            return 'log2(%s)' % repr(self.numerus)

        def gentle_simplify(self):
            # some special values, kind of dumb but not too bad
            if self.numerus == mathify(1):
                return mathify(0)
            if self.numerus == mathify(2):
                return mathify(1)
            return self

        def simplify(self):
            # a better simplify() method would check for do
            # things like log2(2**x).simplify() == x
            return self.gentle_simplify()


    def log2(numerus):
        return Base2Log(numerus).gentle_simplify()


    # minimal tests :D
    print(log2(1))      # 0
    print(Base2Log(1))  # log2(1)
    print(log2(2))      # 1
    print(Base2Log(2))  # log2(2)

    x = Symbol('x')
    print(log2(x))      # log2(x)
    print(Base2Log(x))  # log2(x)

    # these are WRONG!!
    print(log2(x).may_depend_on(x))     # False
    print(log2(x).derivative(x))        # 0
    print(log2(x) == log2(x))           # False

If you are wondering why we need a class and a factory function, check out
:func:`~MathObject.gentle_simplify` documentation (just click the link).

Many things work quite nicely, but something weird is going on with the last
few things. By default, derivater assumes that MathObjects don't depend on
anything. The docs of :meth:`~MathObject.may_depend_on` say that it's best to
override :meth:`~MathObject.apply_to_content` instead of overriding
:meth:`~MathObject.may_depend_on`, so let's do that by almost copy/pasting the
code from the docs::

    class Base2Log(MathObject):
        ...
        def apply_to_content(self, func):
            return log2(func(self.numerus))

Now we can already do lots of stuff, e.g. ``log2(2*x).replace(2*x, y)`` to get
``log2(y)``. The ``log2(x).may_depend_on(x)`` thing now returns ``True``
correctly, but ``log2(x).derivative(x)`` raises an error:

.. code-block:: none

    Traceback (most recent call last):
      ...
    TypeError: cannot take derivative of log2(x) with respect to x

But we know that ``log2`` is a differentiable function, so we could override
:meth:`~MathObject.derivative` to fix this.

We can fix the ``log2(x) == log2(x)`` problem by applying a simple decorator::

    from derivater import eq_and_hash

    @eq_and_hash({'numerus': None})
    class Base2Log(MathObject):
        ...

Here are the docs of :func:`eq_and_hash`.

.. autofunction:: eq_and_hash


Common MathObject Subclasses
----------------------------

It may be useful to inspect these objects. For example, the
``Base2Log.simplify()`` method in :ref:`the above example <log2-class-example>`
might look like this::

    def simplify(self):
        numerus = self.numerus.simplify()
        if isinstance(numerus, Pow) and numerus.base == mathify(2):
            # log2(2**x) == x
            return self.numerus.exponent
        ...more checks here...
        return log2(numerus)    # cannot simplify more :(

.. _addmulpow:

Another reason why you might need to know something about the stuff documented
below is to e.g. add things together *without*
:meth:`~MathObject.gentle_simplify`. For example, ``x + y`` is actually
``Add([x, y]).gentle_simplify()``, but ``Add([x, y])`` is not simplified at
all:

>>> mathify(1) + mathify(2)
3
>>> Add([1, 2])   # mathifies automatically, but doesn't gentle_simplify()
1 + 2

Here's a handy table:

==========  ============================================
This...     ...actually does this
==========  ============================================
``x + y``   ``Add([x, y]).gentle_simplify()``
``-x``      ``Mul([-1, x]).gentle_simplify()``
``x - y``   ``Add([x, Mul([-1, y])]).gentle_simplify()``
``x * y``   ``Mul([x, y]).gentle_simplify()``
``1 / y``   ``Pow(y, -1).gentle_simplify()``
``x / y``   ``Mul([x, Pow(y, -1)]).gentle_simplify()``
``x ** y``  ``Pow(x, y).gentle_simplify()``
==========  ============================================

.. autoclass:: Add
    :members:
.. autoclass:: Mul
    :members:
.. autoclass:: Pow
    :members:
.. autoclass:: Integer
    :members:
