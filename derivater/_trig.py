from derivater._base import MathObject, eq_and_hash, mathify


def trig_func_class(klass):
    def replace(self, old, new):
        return klass(self.arg.replace(old, new))

    klass.__repr__ = lambda self: '%s(%r)' % (klass.__name__, self.arg)
    klass.pow_parenthesize = lambda self: '(' + repr(self) + ')'
    klass.replace = replace
    return klass


@eq_and_hash({'arg': None})
@trig_func_class
class sin(MathObject):
    """The sine function.

    >>> sin(2*x + 1)
    sin(2*x + 1)
    >>> sin(2*x + 1).derivative(x)
    2*cos(2*x + 1)
    """

    def __init__(self, arg):
        self.arg = arg

    def derivative(self, wrt):
        return cos(self.arg) * self.arg.derivative(wrt)


@eq_and_hash({'arg': None})
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


@eq_and_hash({'arg': None})
@trig_func_class
class tan(MathObject):
    """The tangent function, mathematically equal to ``sin(arg) / cos(arg)``.
    """

    def __init__(self, arg):
        self.arg = arg

    def derivative(self, wrt):
        # FIXME: this doesn't work very well
        #
        # >>> sin(2*x)/cos(2*x)
        # sin(2*x) / cos(2*x)
        # >>> _.derivative(x)
        # 2 + 2*(sin(2*x))**2 / (cos(2*x))**2
        # >>> (sin(2*x)/cos(2*x)).derivative(x)
        # 2 + 2*(sin(2*x))**2 / (cos(2*x))**2
        # >>> _.replace(sin(2*x)**2/cos(2*x)**2, tan(2*x)**2)
        # 2*(sin(2*x))**2 / (cos(2*x))**2 + 2
        # >>> _.replace(2*sin(2*x)**2/cos(2*x)**2, 2*tan(2*x)**2)
        # 2*(tan(2*x))**2 + 2
        #
        # this is Mul's fault, it should partially replace args as well
        return (sin(self.arg) / cos(self.arg)).derivative(wrt).replace(
            sin(self.arg)**2 / cos(self.arg)**2, tan(self.arg)**2)
