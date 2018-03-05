import fractions
import functools
import operator

import pytest

from derivater import (MathObject, Add, Mul, Pow, Integer,
                       mathify, pythonify, ln)
from derivater.__main__ import x, y, half


def test_operators():
    pairs = [
        (2*x, y),
        (2*ln(4), y),
        (x, x),
        (x, 2*x),
        (y, -2*x),
        # not all things are MathObjects, they must be mathified
        (1, -2*x),
        (-10, -x),
    ]
    pairs.extend([(b, a) for (a, b) in pairs])

    for a, b in pairs:
        if not isinstance(b, int):
            assert 0 - b == -b
            assert 1 / b == pow(b, -1)

        assert a + b == Add([a, b]).gentle_simplify()
        assert a - b == Add([a, -b]).gentle_simplify()
        assert a * b == Mul([a, b]).gentle_simplify()
        assert a / b == Mul([a, Pow(b, -1)]).gentle_simplify()
        assert a**b == Pow(a, b).gentle_simplify()


def test_replace():
    a = MathObject()
    b = MathObject()
    assert a.replace(a, b) == b


class Toot(MathObject):
    def __init__(self, simplified=False):
        self.simplified = simplified
    def __repr__(self):
        return '<Toot>'
    def simplify(self):
        return Toot(simplified=True)
    def may_depend_on(self, var):
        return (var == y)


def test_default_may_depend_on_and_derivative():
    assert not MathObject().may_depend_on(x)    # must be overrided if depdends

    assert not Toot().may_depend_on(x)
    assert Toot().may_depend_on(y)
    assert Toot().derivative(x) == mathify(0)
    with pytest.raises(TypeError, match=(r"cannot take derivative of <Toot> "
                                         r"with respect to y$")):
        Toot().derivative(y)


class TootContainer(MathObject):
    def __init__(self, content):
        self.content = mathify(content)
    def apply_to_content(self, func):
        return TootContainer(func(self.content))


def test_default_simplify():
    assert TootContainer(Toot()).simplify().content.simplified


def test_mathify_pythonify():
    math2python = {
        Integer(1): 1,
        Integer(1)/2: fractions.Fraction(1, 2),
        Integer(3)/(-5): fractions.Fraction(-3, 5),
        Pow(4, 2): fractions.Fraction(4)**2,
        Pow(5, 3): 5**3,
    }

    # keys() and values() are guaranteed to be in the same order, although a
    # different order shouldn't matter
    math_sum = Add(math2python.keys())      # not gentle_simplify()ied
    python_sum = sum(math2python.values())
    math2python[math_sum] = python_sum

    math_product = Mul(math2python.keys())
    python_product = functools.reduce(operator.mul, math2python.values())
    math2python[math_product] = python_product

    for math, python in math2python.items():
        assert mathify(math) == math        # returned as is
        assert mathify(python) == math.gentle_simplify()
        assert pythonify(math) == python
        assert pythonify(python) == python

    # make sure that fractions aren't returned when not needed
    assert type(mathify(fractions.Fraction(2, 1))) is Integer
    assert type(pythonify(Mul([4, half]))) is int

    with pytest.raises(TypeError, match="don't know how to pythonify <Toot>$"):
        pythonify(Toot())
    with pytest.raises(TypeError, match="don't know how to mathify 'lol'$"):
        mathify('lol')


def test_integers():
    for n in [-10, -1, 0, 1, 10]:
        assert mathify(n) == Integer(n)
        assert mathify(n).python_int == n
        assert not mathify(n).may_depend_on(x)
        assert mathify(n).with_fraction_coeff() == (mathify(n), mathify(1))

        assert not repr(mathify(n)).startswith('(')
        assert not repr(mathify(n)).endswith(')')
        if n < 0:
            assert mathify(n).add_parenthesize().startswith('(-')
            assert mathify(n).add_parenthesize().endswith(')')
        else:
            assert mathify(n).add_parenthesize() == repr(mathify(n)) == repr(n)

    with pytest.raises(TypeError, match=r"cannot create Integer of 'lol'$"):
        Integer('lol')

    # "cannot create Integer of 2" would be a very confusing error message
    with pytest.raises(TypeError,
                       match=r"cannot create a new Integer of an Integer$"):
        Integer(Integer(2))
