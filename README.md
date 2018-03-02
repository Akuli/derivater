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

Like the name of the library suggests, you can take derivatives of different
functions:

```python
>>> (a*x**2 + b*x + c).derivative(x)
2*x*a + b
>>> (x**x).derivative(x)
x**x*(ln(x) + 1)
```

Most common elementary functions are supported.

```python
>>> ln(x).derivative(x)
1 / x
>>> (e**x).derivative(x)
e**x
>>> sin(2*x+1).derivative(x)
2*cos(2*x + 1)
>>> tan(x).derivative(x)        # the result is tan^2(x) + 1, it just looks a bit messy
((sin(x))**2) / ((cos(x))**2) + 1
```

You can also mix in SymbolFunctions like `f` and `g` with no restrictions:

```python
>>> ln(f(x)).derivative(x)
f'(x) / f(x)
>>> f(g(x)).derivative(x)
f'(g(x))*g'(x)
```
