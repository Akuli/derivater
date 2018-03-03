Low-level Stuff
===============

.. currentmodule:: derivater

If you just want to take derivatives of stuff you don't need anything
documented here, but this stuff lets you implement things like custom functions
that work with derivater.


The MathObject Base Class
-------------------------

.. autoclass:: MathObject
   :members:

.. autofunction:: eq_and_hash


Add, Mul and Pow
----------------

.. warning::
    Don't create instances of these classes directly; use :func:`add`,
    :func:`mul` and :func:`pow` instead. These classes are exposed mostly for
    :func:`isinstance` checks. The documentation below lists a bunch of things
    that instances of these classes must satisfy, and :func:`add`, :func:`mul`
    and :func:`pow` take care of the corner cases.

.. autoclass:: Add
.. autoclass:: Mul
.. autoclass:: Pow


Other MathObject Subclasses
---------------------------

.. autoclass:: Integer
