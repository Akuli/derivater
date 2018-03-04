Trig Functions
==============

.. currentmodule:: derivater

There are quite a few things in this module, but the trig stuff is nowhere near
as good as it could be; even ``(sin(x)**2 + cos(x)**2).simplify()``. Don't
expect the trig functions to support anything more than taking derivatives.

.. function:: sin
.. function:: cos
.. function:: tan

    I'm quite sure you know what these are because you're reading this.

    >>> sin(x).derivative(x)
    cos(x)
    >>> cos(x).derivative(x)
    -sin(x)
    >>> tan(x).derivative(x)
    (tan(x))**2 + 1

.. function:: sec(x)
              csc(x)
              cot(x)

    If you don't know what secant, cosecant and cotangent are, skip this stuff.

    These functions just return other functions because I find using them in
    math confusing, but you might be used to using them.

    >>> sec(x)
    1 / cos(x)
    >>> csc(x)
    1 / sin(x)
    >>> cot(x)
    cos(x) / sin(x)

.. function:: asin
              acos
              atan

    These are inverse trig functions. For example, ``asin(x)`` returns the
    inverse sine of ``x``, often written as :math:`\arcsin(x)` or
    :math:`sin^{-1}(x)`.

    Note that inverse trig functions only return angles on specific ranges; for
    example, ``asin(x)`` is always between ``-tau/4`` and ``tau/4``, but
    ``sin(x)`` can take any ``x`` value. This means that ``sin(asin(x))`` is
    always ``x``, but ``asin(sin(x))`` is not.

.. class:: Sine
           Cosine
           Tangent
           ArcSine
           ArcCosine
           ArcTangent

    These are the types of objects returned by functions with similar names,
    and the above factory functions make instances of these and call
    ``gentle_simplify()``. See :meth:`MathObject.gentle_simplify` docs for
    rationale and more details.
