# Derivater

This is a **simple** symbolic calculation library for Python 3.4 or newer. This
library does derivatives well, but check out [sympy](http://www.sympy.org/) if
you want a full-featured symbolic calculation library instead of this.

## Examples

Start Python like this:

    python3 -im derivater

Or like this if you are on Windows:

    py -im derivater

That is roughly equivalent to starting Python normally and then doing this:

```python
>>> import functools
>>> from derivater import *
>>> a = Symbol('a')
>>> b = Symbol('b')
>>> c = Symbol('c')
>>> f = functools.partial(SymbolFunction, 'f')
>>> g = functools.partial(SymbolFunction, 'g')
>>> x = Symbol('x')
>>> y = Symbol('y')
>>> z = Symbol('z')
```

If you can't get the `-im` trick to work, you can just start Python normally
and do this:

```python
>>> from derivater.__main__ import *
```

Symbols are, of course, an important thing in a symbolic calculation library.

```python
>>> x + x
2*x
>>> x + y
x + y
```

You can `+`, `-`, `*`, `/` or `**` symbols however you want:

```python
>>> x * x * x
x**3
>>> (x + 2)**(-1)
1 / (x + 2)
>>> a*x**2 + b*x + c
a*x**2 + b*x + c
```
