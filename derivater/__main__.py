# flake8: noqa
# for interactive use

from functools import partial as _partial
from derivater import *

a = Symbol('a')
b = Symbol('b')
c = Symbol('c')
f = _partial(SymbolFunction, 'f')
g = _partial(SymbolFunction, 'g')
x = Symbol('x')
y = Symbol('y')
z = Symbol('z')