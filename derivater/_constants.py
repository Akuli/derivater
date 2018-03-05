import math

from derivater._base import MathObject


# __eq__ and __hash__ check "a is b" by default, that's good
class NamedConstant(MathObject):
    """Represents a special constant.

    Two big differences between this class and :class:`Symbol` is that two
    NamedConstants with the same name don't compare equal, and NamedConstants
    can be converted to floats.

    >>> NamedConstant('e', 10.0) == e
    False
    >>> float(NamedConstant('x', 10.0))
    10.0
    >>> float(Symbol('x'))
    Traceback (most recent call last):
      ...
    TypeError: float() argument must be a string or a number, not 'Symbol'

    This means that there's exactly one Euler's number, documented as :data:`e`
    above, and if you make another constant called ``e`` it won't be mistakenly
    treated as Euler's number.

    >>> ln(e)
    1
    >>> ln(NamedConstant('e', 10.0))
    ln(e)

    If you want to use e.g. a Greek letter for the name, you can do e.g.
    ``goldenratio = NamedConstant('\\N{greek small letter phi}')`` to get a
    \N{greek small letter phi} constant.

    You can use ``str()`` and ``float()`` to access *name* and *float_value*
    afterwards:

    >>> str(e)
    'e'
    >>> float(e)        # doctest: +ELLIPSIS
    2.71828...
    """

    def __init__(self, name, float_value):
        if not isinstance(name, str):
            raise TypeError("invalid constant name " + repr(name))
        if not isinstance(float_value, float):
            raise TypeError(repr(float_value) + " is not a valid float value")
        self._name = name
        self._float_value = float_value

    def __repr__(self):
        return self._name

    def __float__(self):
        return self._float_value

    # may_depend_on() returns False by default


e = NamedConstant('e', math.e)
try:
    tau = NamedConstant('tau', math.tau)
except AttributeError:
    tau = NamedConstant('tau', 2*math.pi)
pi = tau/2
