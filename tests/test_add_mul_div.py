import functools

from derivater import Symbol, SymbolFunction, Add, Mul, Pow, mathify, ln
from derivater.__main__ import x, y, z, f, g, f_, g_

h = functools.partial(SymbolFunction, 'h')
h_ = functools.partial(h, derivative_count=1)


def test_minus():
    assert isinstance(-x, Mul)
    assert (-x).objects == [mathify(-1), x]
    assert -(-x) == x

    assert isinstance(x-y, Add)
    assert (x-y).objects == [x, -y]


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


def test_pow_repr():
    assert repr(x**y) == 'x**y'
    assert repr(1/x) == '1 / x'
    assert repr(1/(x+y)) == '1 / (x + y)'


def test_automagic_flatten():
    assert ((f(x)*g(x)) * h(x)).objects == [f(x), g(x), h(x)]
    assert ((f(x)+g(x)) + h(x)).objects == [f(x), g(x), h(x)]
    assert (f(x) * (g(x)*h(x))).objects == [f(x), g(x), h(x)]
    assert (f(x) + (g(x)+h(x))).objects == [f(x), g(x), h(x)]


def test_derivatives():
    assert (f(x) + g(x) + h(x)).derivative(x) == f_(x) + g_(x) + h_(x)
    assert (f(x) * g(x) * h(x)).derivative(x) == (
        f_(x)*g(x)*h(x) + g_(x)*f(x)*h(x) + h_(x)*f(x)*g(x))
    assert (f(x)**g(x)).derivative(x) == (
        f(x)**g(x) * (g_(x)*ln(f(x)) + g(x)*f_(x)/f(x)))
