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
>>> from derivativer import *
>>> a = Symbol('a')
>>> b = Symbol('b')
>>> c = Symbol('c')
>>> x = Symbol('x')
>>> y = Symbol('y')
>>> z = Symbol('z')
```

Symbols are, of course, an important thing in a symbolic calculation library.

```python
>>> from derivater import *; x = Symbol('x')
>>> x + x
2*x
>>> x + y
x + y
```

You can `+`, `-`, `*`, `/` or `**` symbols however you want:

```python
>>> from derivater import *; x = Symbol('x')
>>> x * x * x
x**3
>>> (x + 2)**(-1)
1 / (x + 2)
>>> a*x**2 + b*x + c
a*x**2 + b*x + c
```
