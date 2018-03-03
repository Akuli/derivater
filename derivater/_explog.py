import functools

from derivater._base import MathObject, eq_and_hash, mathify
from derivater._constants import e


def exp(exponent):
    """This is equivalent to ``e**exponent``.

    Unlike in Python's ``math`` module, this function is no more precise than a
    plain ``e**x``, and it's there just for people who prefer to write
    ``exp(x)`` instead of ``e**x``.

    >>> exp(x)
    e**x
    >>> exp(x).derivative(x)
    e**x
    """
    return e**exponent


@eq_and_hash(['numerus'])
class NaturalLog(MathObject):
    """The type of many objects returned by :func:`ln`.

    Don't create ``NaturalLog`` objects yourself; use :func:`ln` instead. It
    may return special values like 0 or 1 instead of ``NaturalLog`` objects.

    .. attribute:: numerus

        The object passed to :func:`ln`.
    """

    def __init__(self, numerus):
        assert numerus != 1 and numerus != e
        self.numerus = numerus

    def __repr__(self):
        return 'ln(%r)' % self.numerus

    # explicit is better than implicit, (ln(a))**b is better than ln(a)**b
    def pow_parenthesize(self):
        return '(' + repr(self) + ')'

    def may_depend_on(self, wrt):
        return self.numerus.may_depend_on(wrt)

    def derivative(self, wrt):
        #                   1
        # d/dx ln(f(x)) = ------ * f'(x) = f'(x) / f(x)
        #                  f(x)
        return self.numerus.derivative(wrt) / self.numerus

    def replace(self, old, new):
        old, new = mathify(old), mathify(new)
        if self == old:
            return new
        return ln(self.numerus.replace(old, new))


def ln(numerus):
    """Return the natural logarithm (base :data:`e`) of *numerus*.

    >>> ln(e)
    1
    >>> ln(x).derivative(x)
    1 / x
    >>> (x**x).derivative(x)
    x**x*(ln(x) + 1)
    """
    numerus = mathify(numerus)
    if numerus == mathify(1):
        return mathify(0)
    if numerus == e:
        return mathify(1)
    return NaturalLog(numerus)


def log(numerus, base=e):
    """Return the logarithm of *numerus* with the given *base*.

    This is equivalent to ``ln(numerus) / ln(base)``.

    >>> log(x, 2)
    ln(x) / ln(2)
    >>> log(x)
    ln(x)
    """
    return ln(numerus) / ln(base)


log2 = functools.partial(log, base=2)
log10 = functools.partial(log, base=10)
