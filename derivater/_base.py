import collections


def eq_and_hash(as_is=(), tupled=()):
    """A decorator that adds ``__eq__`` and ``__hash__`` methods to a class.

    If you want to make a :class:`MathObject` subclass that is used like
    this...
    ::
        t = Toot(a, b, [c, d])

    ...then you should also implement ``__eq__`` and ``__hash__``. They should
    treat the objects as equal when they are identical (not just same value),
    e.g. ``ln(x**2) == ln(x**2)`` and ``hash(ln(x**2)) == hash(ln(x**2))``, but
    ``ln(x**2) != 2*ln(x)`` and ``hash(ln(x**2)) != hash(2*ln(x))``. So, our
    ``Toot`` class can be written like this...
    ::

        class Toot(derivater.MathObject):

            def __init__(self, a, b, cdlist):
                self.a = a
                self.b = b
                self.cdlist = cdlist

            def __eq__(self, other):
                if not isinstance(other, Toot):
                    return NotImplemented
                return (self.a == other.a and self.b == other.b and
                        self.cdlist == other.cdlist)

            def __hash__(self):
                # reuse tuple's __hash__, but convert cdlist to a tuple
                # because lists aren't hashable
                return hash((self.a, self.b, tuple(self.cdlist)))

    ...or like this::

        @derivater.eq_and_hash(['a', 'b'], tupled=['cdlist'])
        class Toot(derivater.MathObject):

            def __init__(self, a, b, bclist):
                self.a = a
                self.b = b
                self.cdlist = cdlist
    """
    def get_stuff(instance):
        result = []
        for attr in as_is:
            result.append(getattr(instance, attr))
        for attr in tupled:
            result.append(tuple(getattr(instance, attr)))
        return tuple(result)

    def decorate(klass):
        def eq(self, other):
            if not isinstance(other, klass):
                return NotImplemented
            return get_stuff(self) == get_stuff(other)

        def hash_(self):
            return hash(get_stuff(self))

        klass.__eq__ = eq
        klass.__hash__ = hash_
        return klass

    return decorate


def mathify(obj):
    """Convert a Python number into a :class:`MathObject`.

    If *obj* is already a :class:`MathObject`, it's returned as is.
    """
    if isinstance(obj, MathObject):
        return obj
    if isinstance(obj, int):
        return Integer(obj)
    raise TypeError("don't know how to mathify " + repr(obj))


# MathObjects should be considered immutable
# __eq__'s are not mathy equality, they just check whether two math
# objects are considered very similar, e.g. Symbol('x') == Symbol('x')
class MathObject:
    """Base class for all mathy objects.

    Inherit from this class if you want to make an object that is compatible
    with derivater.

    .. seealso:: :func:`eq_and_hash`

    .. method:: add_parenthesize
                mul_parenthesize
                pow_parenthesize

        Pretty-printing objects is usually implemented with ``__repr__()``. For
        example, :class:`.NaturalLog` does this::

            def __repr__(self):
                return 'ln(%r)' % self.numerus

        However, sometimes parenthesized things are needed. If we have
        ``(x + 1)**y`` it must not be displayed as ``x + 1**y``, but if we have
        ``2**y`` it must not be displayed as ``(2)**y``. These methods let you
        customize how the object is parenthesized. Click the above *[source]*
        links to see what these methods do by default; usually it's enough to
        implement just one of these methods e.g. like this::

            def mul_parenthesize(self):
                return '(' + repr(self) + ')'

        Reprs of :class:`Add`, :class:`Mul` and :class:`Pow` call these methods
        roughly like this:

        * ``repr(x+y) == x.add_parenthesize() + ' + ' + y.add_parenthesize()``
        * ``repr(x*y) == x.mul_parenthesize() + '*' + y.mul_parenthesize()``
        * ``repr(x**y) == x.pow_parenthesize() + '**' + y.pow_parenthesize()``
    """

    # repr()s with parenthesis for Add, Mul and Pow
    def add_parenthesize(self):
        return repr(self)

    def mul_parenthesize(self):
        return self.add_parenthesize()

    def pow_parenthesize(self):
        return self.mul_parenthesize()

    # should return True if not sure
    def may_depend_on(self, var):
        """Check if this variable depends on the value of *var*.

        The *var* should always be a :class:`Symbol`.
        """
        return True

    def replace(self, old, new):
        old, new = mathify(old), mathify(new)
        if self == old:
            return new
        return self

    # everything except stuff with wrt in it are constants
    # wrt should be a Symbol
    def derivative(self, wrt):
        if not self.may_depend_on(wrt):
            return mathify(0)
        raise TypeError("cannot take derivative of %s" % type(self).__name__)

    def __add__(self, other):   # self + other
        return add([self, other])

    __radd__ = __add__          # other + self

    def __neg__(self):          # -self
        return mul([-1, self])

    def __sub__(self, other):   # self - other
        return self + (-other)

    def __rsub__(self, other):  # other - self
        return other + (-self)

    def __mul__(self, other):   # self * other
        return mul([self, other])

    __rmul__ = __mul__          # other * self

    def __truediv__(self, other):   # self / other
        # it's important to mathify the -1 because 2**(-1) == 0.5, but
        # we don't want floats
        return self * other**(mathify(-1))

    def __rtruediv__(self, other):  # other / self
        # -1 will be mathified automatically by __pow__
        return other * self**(-1)

    def __pow__(self, other):   # self ** other
        return pow(self, other)

    def __rpow__(self, other):  # other ** self
        return pow(other, self)


@eq_and_hash(['name'])
class Symbol(MathObject):
    """A symbol like ``x`` or ``y``.

    >>> x = Symbol('x')
    >>> x
    x
    >>> 1 + x*x
    x**2 + 1

    You can use Symbols freely with all derivater functions, but Python's
    built-in functions don't usually like them:

    >>> sin(x)
    sin(x)
    >>> import math
    >>> math.sin(x)
    Traceback (most recent call last):
      ...
    TypeError: must be real number, not Symbol
    """

    def __init__(self, name):
        if not isinstance(name, str):
            raise TypeError("Symbol(%s)" % type(name).__name__)
        self.name = name

    def __repr__(self):
        return self.name

    # two symbols with same name are considered equal, temporary symbols
    # that don't do this (see sympy's Dummy class) may be needed later
    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.name == other.name
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

    def may_depend_on(self, other_symbol):
        return (self == other_symbol)

    def derivative(self, wrt):
        if wrt == self:
            return 1
        else:
            return 0


class SymbolFunction(MathObject):
    """Represents an unknown, single-variable function.

    >>> from derivater import SymbolFunction, Symbol
    >>> x = Symbol('x')
    >>> SymbolFunction('f', x)
    f(x)
    >>> SymbolFunction('g', x)
    g(x)

    Use :func:`functools.partial` if you want to type ``f(x)`` to get ``f(x)``:

    >>> from functools import partial
    >>> f = partial(SymbolFunction, 'f')
    >>> g = partial(SymbolFunction, 'g')
    >>> f(x)
    f(x)

    You can e.g. take derivatives of SymbolFunctions nicely.

    >>> SymbolFunction('f', x, derivative_count=2)
    f''(x)
    >>> f(x, derivative_count=2)
    f''(x)
    >>> f(x).derivative().derivative()
    f''(x)
    >>> (f(x) * g(x)).derivative(x)
    f'(x)*g(x) + g'(x)*f(x)
    >>> f(g(x)).derivative(x)
    f'(g(x))*g'(x)
    """

    def __init__(self, name, arg, *, derivative_count=0):
        self.name = name
        self.arg = arg
        self.derivative_count = derivative_count

    def __repr__(self):
        return '%s%s(%r)' % (
            self.name, "'" * self.derivative_count, self.arg)

    def may_depend_on(self, wrt):
        return self.arg.may_depend_on(wrt)

    def derivative(self, wrt):
        return (SymbolFunction(self.name, self.arg,
                               derivative_count=self.derivative_count+1)
                * self.arg.derivative(wrt))


# low-level integer
@eq_and_hash(['python_int'])
class Integer(MathObject):
    """An integer with a known value.

    You can create Integer objects yourself or, equivalently, you can pass a
    Python int to :func:`mathify`.
    """

    def __init__(self, python_int):
        assert isinstance(python_int, int)
        self.python_int = python_int

    def __repr__(self):
        return str(self.python_int)

    def __eq__(self, other):
        if isinstance(other, Integer):
            return self.python_int == other.python_int
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.python_int)

    def may_depend_on(self, var):   # enough for derivative() to work
        return False

    def add_parenthesize(self):
        if self.python_int < 0:
            return '(' + repr(self) + ')'
        return repr(self)


def _looks_like_negative(expr):
    if isinstance(expr, Mul):
        return (isinstance(expr.objects[0], Integer) and
                expr.objects[0].python_int < 0)
    if isinstance(expr, Integer):
        return expr.python_int < 0
    return False


@eq_and_hash(tupled=['objects'])
class Add(MathObject):
    """An object that represents a bunch of things added together.

    All ``Add`` objects should satisfy these things:

    * There's never an ``Add`` directly inside an ``Add``;
      ``Add([a, b, Add([c, d])])`` is expaneded to ``Add([a, b, c, d])``.
    * The list of added objects is accessible as ``add_object.objects`` and it
      always contains at least 2 elements.
    * The object list does not contain zeros.
    * The object list can contain at most 1 :class:`Integer`.
    * If the object list contains an integer, it's ``objects[0]``.

    Substraction like ``a - b`` is represented as
    ``Add([a, Mul([Integer(-1), b])])``.

    .. attribute:: objects

        List of the added objects.
    """

    def __init__(self, objects):
        assert len(objects) >= 2
        self.objects = objects

    def __repr__(self):
        result = [self.objects[0].add_parenthesize()]

        for obj in self.objects[1:]:
            if _looks_like_negative(obj):
                result.append(' - ')
                result.append((-obj).add_parenthesize())
            else:
                result.append(' + ')
                result.append(obj.add_parenthesize())
        return ''.join(result)

    def __eq__(self, other):
        if not isinstance(other, Add):
            return NotImplemented
        return self.objects == other.objects

    def __hash__(self):
        return hash(tuple(self.objects))

    def mul_parenthesize(self):
        return '(' + repr(self) + ')'

    def may_depend_on(self, wrt):
        return any(obj.may_depend_on(wrt) for obj in self.objects)

    def replace(self, old, new):
        old, new = mathify(old), mathify(new)
        if self == old:
            return new
        return add(obj.replace(old, new) for obj in self.objects)

    def derivative(self, wrt):
        # d/dx (f(x) + g(x)) = f'(x) + g'(x)
        # also works with more than 2 functions
        return add(obj.derivative(wrt) for obj in self.objects)


@eq_and_hash(tupled=['objects'])
class Mul(MathObject):
    """An object that represents a bunch of stuff multiplied with each other.

    All ``Mul`` objects should satisfy these things:

        * There's never a ``Mul`` directly inside a ``Mul``;
          ``Mul([a, b, Mul([c, d])])`` is expaneded to ``Mul([a, b, c, d])``.
        * The list of multiplied objects is accessible as
          ``mul_object.objects`` and it always contains at least 2 elements.
        * The object list does not contain ones or zeros.
        * The object list can contain at most 1 integer (positive or negative).
        * If the object list contains an integer, it's ``objects[0]``.

    .. attribute:: objects

        List of the multiplied objects.
    """

    def __init__(self, objects):
        assert len(objects) >= 2
        self.objects = objects

    def __repr__(self):
        # TODO: a/b is represented as a*b**(-1), maybe display them with
        # division here?
        if _looks_like_negative(self):
            return '-' + (-self).mul_parenthesize()

        # a/b is represented as a*b**(-1)
        top = []
        bottom = []
        for obj in self.objects:
            if isinstance(obj, Pow) and _looks_like_negative(obj.exponent):
                # 1/obj is the same thing with inverted exponent
                bottom.append(1/obj)
            else:
                top.append(obj)

        if not bottom:
            assert len(top) >= 2
            return '*'.join(obj.mul_parenthesize() for obj in top)

        return (mul(top).pow_parenthesize() + ' / ' +
                mul(bottom).pow_parenthesize())

    def __eq__(self, other):
        if not isinstance(other, Mul):
            return NotImplemented
        return self.objects == other.objects

    def __hash__(self):
        return hash(tuple(self.objects))

    def pow_parenthesize(self):
        return '(' + repr(self) + ')'

    def may_depend_on(self, wrt):
        return any(obj.may_depend_on(wrt) for obj in self.objects)

    def replace(self, old, new):
        old, new = mathify(old), mathify(new)
        if self == old:
            return new
        return mul(obj.replace(old, new) for obj in self.objects)

    def derivative(self, wrt):
        # d/dx (f(x)g(x)h(x)) = f'(x)g(x)h(x) + f(x)g'(x)h(x) + f(x)g(x)h'(x)
        # it works like this for more functions, derivative of each
        # function multiplied by all other functions
        parts = []
        for i in range(len(self.objects)):      # OMG ITS RANGELEN KITTENS DIE
            others = self.objects[:i] + self.objects[i+1:]
            parts.append(self.objects[i].derivative(wrt) * mul(others))
        return add(parts)


# low-level base**exponent object
#   * (x**y)**z is not allowed, must be converted to x**(y*z)
#   * base and exponent must not be 1
#   * division is represented with Pow(x, mathify(-1))
@eq_and_hash(['base', 'exponent'])
class Pow(MathObject):
    """An object that represents ``base ** exponent``.

    All ``Pow`` objects should satisfy these things:

        * The base cannot be a ``Pow`` object; ``(x**y)**z`` must be converted
          to ``x**(y*z)``.
        * The base and the exponent must not be 1.

    Division is represented as ``Pow(x, something_negative)``.

    .. attribute:: base
                   exponent

        Pow objects represent ``base**exponent``.

    """

    def __init__(self, base, exponent):
        assert base != mathify(1) and exponent != mathify(1)
        assert not isinstance(base, Pow)
        self.base = base
        self.exponent = exponent

    def __repr__(self):
        if self.exponent == mathify(-1):
            return '1 / ' + self.base.pow_parenthesize()
        return (self.base.pow_parenthesize() + '**' +
                self.exponent.pow_parenthesize())

    def pow_parenthesize(self):
        # x**y**z = x**(y**z)
        # that's why (x**y)**z must be shown with parentheses around x**y
        return '(' + repr(self) + ')'

    def may_depend_on(self, wrt):
        return self.base.may_depend_on(wrt) or self.exponent.may_depend_on(wrt)

    def replace(self, old, new):
        old, new = mathify(old), mathify(new)
        if self == old:
            return new
        return self.base.replace(old, new) ** self.exponent.replace(old, new)

    def derivative(self, wrt):
        # _explog.py wants lots of stuff from this file
        # this file wants exp and ln from _explog.py
        from derivater._explog import exp, ln

        if not self.may_depend_on(wrt):
            return mathify(0)
        if not self.base.may_depend_on(wrt):
            # d/dx a**f(x) = a**f(x) ln(a) * f'(x)
            return self * ln(self.base) * self.exponent.derivative(wrt)
        if not self.exponent.may_depend_on(wrt):
            # d/dx f(x)**c = c*f(x)**(c-1) * f'(x)
            # must be handled specially because this is defined if self.base
            # is negative and self.exponent is an integer, but the stuff below
            # needs ln(self.base)
            return (self.exponent * self.base**(self.exponent - 1) *
                    self.base.derivative(wrt))

        #                  /     g(x) \
        #     g(x)       ln| f(x)     |      g(x)*ln(f(x))
        # f(x)      =  e   \          /  =  e
        #
        # rest of the code can take the derivative of that
        rewrite = exp(self.exponent * ln(self.base))
        result = rewrite.derivative(wrt)
        return result.replace(rewrite, self)    # a bit simpler


# high-level constructors
# the docstrings say that these are equivalent to something with
# operators, but the operator stuff just calls these (see MathObject)
def add(objects):
    """Add together an iterable of :class:`MathObjects <MathObject>`.

    This is equivalent to ``mathify(objects[0]) + mathify(objects[1]) + ... + \
mathify(objects[len(objects)-1])``.
    """
    flattened = []
    for obj in map(mathify, objects):
        if isinstance(obj, Add):
            flattened.extend(obj.objects)
        elif obj != mathify(0):
            flattened.append(obj)

    # extract integers
    # this is kind of tricky because -2 is represented as (-1)*2
    int_value = 0
    not_integers = []
    for obj in flattened:
        if isinstance(obj, Integer):
            int_value += obj.python_int
        else:
            not_integers.append(obj)

    # turn repeated objects into _Muls until nothing is repeated
    result = not_integers
    old_result = None
    while result != old_result:
        old_result = result
        result = list(map(mul, collections.Counter(result).items()))

    # don't turn x*y + y into (x + 1)*y,
    # it wouldn't be too bad to combine integer coefficients though, e.g.
    # like 2*x + 3*x == 5*x

    # integer value goes last
    if int_value != 0:
        result.append(mathify(int_value))

    if not result:
        return mathify(0)
    if len(result) == 1:
        return result[0]
    return Add(result)


def _stupid_grouper(types, objects):
    result = {klass: [] for klass in types}
    result[None] = []

    for obj in objects:
        for klass in types:
            if isinstance(obj, klass):
                result[klass].append(obj)
                break
        else:
            result[None].append(obj)    # no type

    return result


def mul(objects):
    """Multiply together an iterable of :class:`MathObjects <MathObject>`.

    This is equivalent to ``mathify(objects[0]) * mathify(objects[1]) * ... * \
mathify(objects[len(objects)-1])``.
    """
    flattened = []
    for obj in map(mathify, objects):
        if isinstance(obj, Mul):
            flattened.extend(obj.objects)
        elif obj == mathify(0):
            return mathify(0)
        else:
            flattened.append(obj)

    # extract integers
    int_value = 1
    not_integers = []
    for value in flattened:
        if isinstance(value, Integer):
            int_value *= value.python_int
        else:
            not_integers.append(value)

    # turn repeated objects into _Pows and group together _Pows with same base
    powers = {}      # {base: exponent}
    for obj in not_integers:
        if isinstance(obj, Pow):
            base = obj.base
            exponent = obj.exponent
        else:
            base = obj
            exponent = mathify(1)
        powers[base] = powers.get(base, mathify(0)) + exponent

    result = [pow(base, exponent) for base, exponent in powers.items()]

    # integer coefficient goes first
    if int_value != 1:
        result = [Integer(int_value)] + result

    if not result:
        return mathify(1)
    if len(result) == 1:
        return result[0]
    return Mul(result)


# TODO: disallow zero division, now we have    mathify(1) / 0 * 0 == 0
def pow(base, exponent):
    """This is equivalent to ``mathify(base) ** mathify(exponent)``."""
    base = mathify(base)
    exponent = mathify(exponent)

    if isinstance(base, Pow):
        return pow(base.base, base.exponent * exponent)
    if base == mathify(1):
        return mathify(1)
    if exponent == mathify(1):
        return base
    if exponent == mathify(0):
        # python does 0**0 == 1... it can't be too bad not to handle
        # base==0 specially
        return mathify(1)
    if (isinstance(base, Integer) and
            isinstance(exponent, Integer) and
            (exponent.python_int >= 0 or base == mathify(-1))):
        # we know for sure it'll be an integer
        # TODO: handle more corner cases
        return mathify(round(base.python_int ** exponent.python_int))
    return Pow(base, exponent)
