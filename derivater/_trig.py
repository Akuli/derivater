from derivater._base import MathObject, eq_and_hash, mathify


@eq_and_hash(['arg'])
class sin(MathObject):
    """The sine function."""

    def __init__(self, arg):
        self.arg = arg

    def __repr__(self):
        return 'sin(%r)' % self.arg

    def pow_parenthesize(self):
        return '(' + repr(self) + ')'

    def replace(self, old, new):
        old, new = mathify(old), mathify(new)
        if self == old:
            return new
        return sin(self.arg.replace(old, new))

    def derivative(self, wrt):
        return cos(self.arg) * self.arg.derivative(wrt)


@eq_and_hash(['arg'])
class cos(MathObject):
    """The cosine function."""

    def __init__(self, arg):
        self.arg = arg

    def __repr__(self):
        return 'cos(%r)' % self.arg

    def pow_parenthesize(self):
        return '(' + repr(self) + ')'

    def replace(self, old, new):
        old, new = mathify(old), mathify(new)
        if self == old:
            return new
        return cos(self.arg.replace(old, new))

    def derivative(self, wrt):
        return -sin(self.arg) * self.arg.derivative(wrt)


def tan(x):
    return sin(x) / cos(x)
