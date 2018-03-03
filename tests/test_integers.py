import derivater

x = derivater.Symbol('x')


def test_integers():
    for n in [-10, -1, 0, 1, 10]:
        assert derivater.mathify(n) == derivater.Integer(n)
        assert derivater.mathify(n).python_int == n
        assert not derivater.mathify(n).may_depend_on(x)
