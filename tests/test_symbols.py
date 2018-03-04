import functools

import pytest

from derivater import Symbol, SymbolFunction, mathify
from derivater.__main__ import x, y, f, g, f_, g_
f__ = functools.partial(f, derivative_count=2)


def test_reprs():
    assert repr(x) == 'x'
    assert repr(f(x)) == 'f(x)'
    assert repr(f(x, derivative_count=2)) == "f''(x)"


def test_eqs_and_hashes(hasheq):
    assert hasheq(x, x)
    assert not hasheq(x, y)

    assert hasheq(f(x), f(x))
    assert hasheq(f_(x), f_(x))
    assert not hasheq(f(x), f(y))
    assert not hasheq(f(x), f_(x))
    assert not hasheq(f(x), g(x))


def test_may_depend_on():
    assert x.may_depend_on(x)
    assert not x.may_depend_on(y)
    assert f(x).may_depend_on(x)
    assert not f(x).may_depend_on(y)


def test_derivatives():
    with pytest.raises(ValueError,
                       match="negative derivative_count is not supported$"):
        f(x, derivative_count=-1)

    assert x.derivative(x) == mathify(1)
    assert x.derivative(y) == mathify(0)
    assert f(x).derivative(x) == f_(x)
    assert f(x).derivative(x).derivative(x) == f__(x)
    assert f(x).derivative(y) == mathify(0)
    assert f(g(x)).derivative(x) == f_(g(x))*g_(x), "u forgot chain rule n00b"


def test_automagic_mathify():
    assert f(2).arg == mathify(2)
