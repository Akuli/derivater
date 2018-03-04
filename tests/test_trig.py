import pytest

from derivater import sin, cos, tan
from derivater.__main__ import f, f_, x, y


def test_trig_func_class_stuff():
    for name, func in [('sin', sin), ('cos', cos), ('tan', tan)]:
        assert func(2*x).arg == 2*x
        with pytest.raises(TypeError):
            func(x, y)
        assert repr(func(x)) == name + '(x)'
        assert func(f(x)).replace(f(x), y) == func(y)   # test apply_to_content
        assert func(x).pow_parenthesize() == '(%s(x))' % name


def test_trig_derivatives():
    assert sin(x).derivative(x) == cos(x)
    assert cos(x).derivative(x) == -sin(x)
    assert tan(x).derivative(x) == 1 + tan(x)**2

    assert sin(f(x)).derivative(x) == cos(f(x))*f_(x)
    assert cos(f(x)).derivative(x) == -sin(f(x))*f_(x)
    assert tan(f(x)).derivative(x) == f_(x) + f_(x)*tan(f(x))**2
