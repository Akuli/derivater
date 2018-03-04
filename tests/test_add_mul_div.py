import functools

from derivater import (eq_and_hash, MathObject, Symbol, SymbolFunction,
                       Add, Mul, Pow, mathify, ln)
from derivater.__main__ import x, y, z, a, b, f, g, f_, g_

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


def test_mul_repr():
    assert repr(-x) == '-x'
    assert repr(2*x) == '2*x'
    assert repr(-2*x) == '-2*x'
    assert repr((x + y)*z) == '(x + y)*z'
    assert repr((x + y)/z) == '(x + y) / z'
    assert repr(Mul([1/x, 1/y])) == '1 / (x*y)'


def test_pow_repr():
    assert repr(x**y) == 'x**y'
    assert repr(1/x) == '1 / x'
    assert repr(1/(x+y)) == '1 / (x + y)'


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
    for even in [-4, -2, 0, 2, 4]:
        assert Pow(-1, even).gentle_simplify() == mathify(1)
    for odd in [-3, -1, 1, 3]:
        assert Pow(-1, odd).gentle_simplify() == mathify(-1)


# i have struggled with these in the past
def test_old_gentle_simplify_bugs():
    assert x + y - x == y
    assert x + 1 - x == mathify(1)
    assert x * y / x == y
    assert x / x == mathify(1)
    assert (x * y)**z == x**z * y**z


def test_derivatives():
    assert (f(x) + g(x) + h(x)).derivative(x) == f_(x) + g_(x) + h_(x)
    assert (f(x) * g(x) * h(x)).derivative(x) == (
        f_(x)*g(x)*h(x) + f(x)*g_(x)*h(x) + f(x)*g(x)*h_(x))
    assert (f(x)**g(x)).derivative(x) == (
        f(x)**g(x) * (g_(x)*ln(f(x)) + g(x)*f_(x)/f(x)))
