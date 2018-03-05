import functools

import pytest

from derivater import (eq_and_hash, MathObject, Symbol, SymbolFunction,
                       Add, Mul, Pow, mathify, ln)
from derivater.__main__ import x, y, z, a, b, f, g, f_, g_, half

h = functools.partial(SymbolFunction, 'h')
h_ = functools.partial(h, derivative_count=1)


def test_minus():
    assert isinstance(-x, Mul)
    assert (-x).objects == [mathify(-1), x]
    assert -(-x) == x

    assert isinstance(x-y, Add)
    assert (x-y).objects == [x, -y]


def equal(a, b):
    return a == b and hash(a) == hash(b)


def test_eq_and_hash_usage():
    assert equal(x+y+z, z+y+x)
    assert equal(x-y-z, -z-y+x)
    assert equal(x*y*z, z*y*x)
    assert equal(x/y/z, 1/z/y*x)


# TODO: check all corner cases!!!
def test_add_repr():
    assert repr(x+y) == 'x + y'
    assert repr(x-y) == 'x - y'
    assert repr(-x-y) == '-x - y'

    assert repr(Add([])) == '0'
    assert repr(Add([-x])) == '-x'
    assert repr(Add([x])) == 'x'


def test_mul_repr():
    assert repr(-x) == '-x'
    assert repr(2*x) == '2*x'
    assert repr(-2*x) == '-2*x'
    assert repr((x + y)*z) == '(x + y)*z'
    assert repr((x + y)/z) == '(x + y) / z'
    assert repr(Mul([1/x, 1/y])) == '1 / (x*y)'

    assert repr(Mul([])) == '1'
    assert repr(Mul([x])) == 'x'
    assert repr(Mul([1/x])) == repr(1/x) == '1 / x'
    assert repr(Mul([Pow(x/y, -2)])) == '1 / (x**2 / y**2)'


class Toot(MathObject):

    def __init__(self, when_to_parenthesize):
        setattr(self, when_to_parenthesize + '_parenthesize', self._parens)

    def __repr__(self):
        return 'T'

    def _parens(self):
        return '(' + repr(self) + ')'


def test_pow_repr():
    assert repr(x**y) == 'x**y'
    assert repr(1/(x+y)) == '1 / (x + y)'

    # 2/something is a Mul, they are here for checking consistency
    assert repr(1/Toot('add')) == '1 / (T)'
    assert repr(2/Toot('add')) == '2 / (T)'
    assert repr(1/Toot('mul')) == '1 / (T)'
    assert repr(2/Toot('mul')) == '2 / (T)'
    assert repr(1/Toot('pow')) == '1 / T'
    assert repr(2/Toot('pow')) == '2 / T'

    # dividing by a Mul is handled specially
    thing1 = Pow(2*Toot('pow'), -1)
    thing2 = 1/(2*Toot('pow'))
    assert isinstance(thing1, Pow)
    assert isinstance(thing2, Mul)
    assert repr(thing1) == '1 / (2*T)'
    assert repr(thing2) == '1 / (2*T)'


@eq_and_hash({'gentle': None})
class Thing(MathObject):

    def __init__(self, gentle=False):
        self.gentle = gentle

    def gentle_simplify(self):
        return Thing(gentle=True)


def test_automagic_gentle_simplify():
    assert (Thing() + x).objects[0].gentle
    assert (Thing() * x).objects[0].gentle
    assert (Thing() ** x).base.gentle
    assert (x ** Thing()).exponent.gentle

    assert not Add([Thing(), x]).objects[0].gentle
    assert not Mul([Thing(), x]).objects[0].gentle
    assert not Pow(Thing(), x).base.gentle
    assert not Pow(x, Thing()).exponent.gentle


def test_add_with_fraction_coeff():
    pass        # tests pass, great!


def test_add_gentle_simplify():
    assert Add([x, y, Thing()]).gentle_simplify() == Add([x, y, Thing(True)])
    assert (Add([x, y, Add([z, Thing()])]).gentle_simplify() ==
            Add([x, y, z, Thing(True)]))
    assert Add([1, x, 2, y, 3]).gentle_simplify() == Add([x, y, 6])
    assert Add([1, x, 2, y, 3]).gentle_simplify().objects[-1] == mathify(6)
    assert Add([x, x, y]).gentle_simplify() == Add([2*x, y])
    assert Add([2*x, 3*y, 4*x]).gentle_simplify() == Add([6*x, 3*y])
    assert Add([x, x]).gentle_simplify() == 2*x
    assert Add([y]).gentle_simplify() == y
    assert Add([2*x, -2*x]).gentle_simplify() == mathify(0)
    assert Add([]).gentle_simplify() == mathify(0)

    assert Add([2, x, half]).gentle_simplify().objects == [x, half*5]
    assert Add([3*x, half*x]).gentle_simplify() == half*7*x

    # these were broken in old derivater versions
    assert Add([x, y, -x]).gentle_simplify() == y
    assert Add([x, -x]).gentle_simplify() == mathify(0)


def test_mul_gentle_simplify():
    assert Mul([x, y, Thing()]).gentle_simplify() == Mul([x, y, Thing(True)])
    assert (Mul([x, y, Mul([z, Thing()])]).gentle_simplify() ==
            Mul([x, y, z, Thing(True)]))
    assert Mul([1, x, 2, y, 3]).gentle_simplify() == Mul([6, x, y])
    assert Mul([1, x, 2, y, 3]).gentle_simplify().objects[0] == mathify(6)
    assert Mul([1, x, y]).gentle_simplify() == Mul([x, y])
    assert (Mul([x, y, x**a, y, x**b]).gentle_simplify() ==
            Mul([x**(a+b+1), y**2]))
    assert Mul([x]).gentle_simplify() == x
    assert Mul([x, x]).gentle_simplify() == x**2
    assert Mul([]).gentle_simplify() == mathify(1)
    assert Mul([x, 1/x]).gentle_simplify() == mathify(1)

    # these were broken in old derivater versions
    assert Mul([x, y, 1/x]).gentle_simplify() == y
    assert Mul([x, 1/x]).gentle_simplify() == mathify(1)


def test_pow_gentle_simplify():
    # these simplify to 0 and 1
    weird0 = Add([x, -x])
    weird1 = Mul([x, 1/x])
    assert weird0 != mathify(0)
    assert weird1 != mathify(1)
    assert weird0.gentle_simplify() == mathify(0)
    assert weird1.gentle_simplify() == mathify(1)

    assert Pow(x, Thing()).gentle_simplify() == Pow(x, Thing(True))
    assert Pow(Thing(), y).gentle_simplify() == Pow(Thing(True), y)
    assert Pow(Pow(x, y), z).gentle_simplify() == Pow(x, y*z)
    assert Pow(x*y, z).gentle_simplify() == Mul([Pow(x, z), Pow(y, z)])
    assert Pow(weird0, x).gentle_simplify() == mathify(0)
    assert Pow(weird1, x).gentle_simplify() == mathify(1)
    assert Pow(weird0, weird0).gentle_simplify() == mathify(0**0)
    assert Pow(x, weird0).gentle_simplify() == mathify(1)
    assert Pow(x, weird1).gentle_simplify() == x

    assert Pow(2, 3).gentle_simplify() == mathify(8)
    assert isinstance(Pow(2, -3).gentle_simplify(), Pow)

    for base in range(-10, 10):
        for exponent in range(-10, 10):
            try:
                value = base**exponent
            except ZeroDivisionError:
                continue    # TODO: derivater should also raise an error :(

            simplified = Pow(base, exponent).gentle_simplify()
            if abs(value - int(value)) > 1e-12:
                # not an integer
                assert isinstance(simplified, Pow)
            else:
                assert simplified == mathify(int(value))


def test_add_partial_replaces():
    # this checks .objects to make sure the order is correct
    assert Add([x, y, z]).replace(Add([x, y]), a).objects == [a, z]
    assert Add([x, y, z]).replace(Add([y, x]), a).objects == [a, z]
    assert Add([x, y, z]).replace(Add([y, z]), a).objects == [x, a]
    assert Add([x, y, z]).replace(Add([z, y]), a).objects == [x, a]
    assert Add([x, y, z]).replace(Add([x, z]), a).objects == [y, a]
    assert Add([x, y, z]).replace(Add([z, x]), a).objects == [a, y]

    assert Mul([x, y, z]).replace(Mul([x, y]), a).objects == [a, z]
    assert Mul([x, y, z]).replace(Mul([y, x]), a).objects == [a, z]
    assert Mul([x, y, z]).replace(Mul([y, z]), a).objects == [x, a]
    assert Mul([x, y, z]).replace(Mul([z, y]), a).objects == [x, a]
    assert Mul([x, y, z]).replace(Mul([x, z]), a).objects == [y, a]
    assert Mul([x, y, z]).replace(Mul([z, x]), a).objects == [a, y]

    for klass, name, instead in [(Add, 'Add', 'zeros'), (Mul, 'Mul', 'ones')]:
        with pytest.raises(ValueError,
                           match=((r"cannot replace %s\(\[\]\) by something, "
                                   r"maybe use gentle_simplify\(\) to turn "
                                   r"%s\(\[\]\)'s into %s\?$")
                                   % (name, name, instead))):
            klass([x, y]).replace(klass([]), z)

    # make sure that gentle_simplify() is not called
    assert not Add([x, y, z]).replace(x+y, Thing()).objects[0].gentle
    assert not Mul([x, y, z]).replace(x*y, Thing()).objects[0].gentle

    # even -x which is Mul([-1, x]) doesn't turn into Integer(-1), instead it
    # turns into Mul([-1, 1]) which looks a lot like Integer(-1) ...  (lol)
    assert Add([x, -x]).replace(x, 1) == Add([1, Mul([-1, 1])])
    assert Mul([x, -x]).replace(x, 1) == Mul([1, Mul([-1, 1])])


def test_derivatives():
    assert (f(x) + g(x) + h(x)).derivative(x) == f_(x) + g_(x) + h_(x)
    assert (f(x) * g(x) * h(x)).derivative(x) == (
        f_(x)*g(x)*h(x) + f(x)*g_(x)*h(x) + f(x)*g(x)*h_(x))
    assert (f(x)**g(x)).derivative(x) == (
        f(x)**g(x) * (g_(x)*ln(f(x)) + g(x)*f_(x)/f(x)))
