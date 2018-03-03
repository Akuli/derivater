from derivater._base import MathObject, eq_and_hash, mathify


def trig_func_class(klass):
    def replace(self, old, new):
        old, new = mathify(old), mathify(new)
        if self == old:
            return new
        return sin(self.arg.replace(old, new))

    klass.__repr__ = lambda self: '%s(%r)' % (klass.__name__, self.arg)
    klass.pow_parenthesize = lambda self: '(' + repr(self) + ')'
    klass.replace = replace
    return klass


@eq_and_hash(['arg'])
@trig_func_class
class sin(MathObject):
    """The sine function.

    >>> sin(2*x + 1)
    2*x + 1
    >>> sin(2*x + 1).derivative(x)
    2*cos(2*x + 1)
    """

    def __init__(self, arg):
        self.arg = arg

    def derivative(self, wrt):
        return cos(self.arg) * self.arg.derivative(wrt)


@eq_and_hash(['arg'])
@trig_func_class
class cos(MathObject):
    """The complement sine function, mathematically equal to ``sin(tau/4 - arg\
)``.

    >>> cos(x).derivative(x)
    -sin(x)
    """

    def __init__(self, arg):
        self.arg = arg

    def derivative(self, wrt):
        return -sin(self.arg) * self.arg.derivative(wrt)


@eq_and_hash(['arg'])
@trig_func_class
class tan(MathObject):
    """The tangent function, mathematically equal to ``sin(arg) / cos(arg)``.
    """

    def __init__(self, arg):
        self.arg = arg

    def derivative(self, wrt):
        # FIXME: replace is broken, .replace sin^2/cos^2 with self**2 when it's
        #        fixed
        return (sin(self.arg) / cos(self.arg)).derivative(wrt)
