from derivater._base import MathObject


# __eq__ and __hash__ check "a is b" by default, that's good
class NamedConstant(MathObject):
    """Represents a constant with a name.

    The biggest difference between this class and :class:`Symbol` is that
    two NamedConstants with the same name don't compare equal:

    >>> NamedConstant('e') == e
    False

    This means that there's exactly one Euler's number, documented as :data:`e`
    above, and if you make another constant called ``e`` it won't be mistakenly
    treated as ``1``:

    >>> ln(e)
    1
    >>> ln(NamedConstant('e'))
    ln(e)

    If you want to use e.g. a Greek letter for the name, you can do e.g.
    ``goldenratio = NamedConstant('\\N{greek small letter phi}')`` to get a
    \N{greek small letter phi} constant.
    """

    def __init__(self, name):
        if not isinstance(name, str):
            raise TypeError("invalid constant name " + repr(name))
        self.name = name

    def __repr__(self):
        return self.name

    # may_depend_on() returns False by default


e = NamedConstant('e')
tau = NamedConstant('tau')
pi = tau/2
