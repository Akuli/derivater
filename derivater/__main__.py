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
