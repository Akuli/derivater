import pytest

from derivater import MathObject, Add, Mul, Pow, mathify, ln
from derivater.__main__ import x, y


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
        assert a / b == a * Pow(b, -1)
        assert a**b == Pow(a, b).gentle_simplify()


def test_replace():
    a = MathObject()
    b = MathObject()
    assert a.replace(a, b) == b


class Toot(MathObject):
    def __repr__(self):
        return '<Toot>'
    def may_depend_on(self, var):
        return (var == y)


def test_default_may_depend_on_and_derivative():
    assert not MathObject().may_depend_on(x)    # must be overrided if depdends

    assert not Toot().may_depend_on(x)
    assert Toot().may_depend_on(y)
    assert Toot().derivative(x) == mathify(0)
    with pytest.raises(TypeError,
                       match=("cannot take derivative of <Toot> "
                              "with respect to y$")):
        Toot().derivative(y)
