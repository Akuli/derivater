# flake8: noqa
# for interactive use

from functools import partial as _partial
from derivater import *

a = Symbol('a')
b = Symbol('b')
c = Symbol('c')
f = _partial(SymbolFunction, 'f')
g = _partial(SymbolFunction, 'g')
f_ = _partial(f, derivative_count=1)
g_ = _partial(g, derivative_count=1)
x = Symbol('x')
y = Symbol('y')
z = Symbol('z')

# 1/2 returns a float :( type half instead, e.g. (half*x**2).derivative(x)
# it's enough to mathify one of the objects, the other will be converted
# automatically
half = mathify(1) / 2
