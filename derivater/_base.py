import collections
import fractions
import functools
import math
import operator

try:
    from math import gcd
except ImportError:     # pragma: no cover
    from fractions import gcd


def eq_and_hash(converters):
    """A decorator that adds ``__eq__`` and ``__hash__`` methods to a class.

    If you want to make a MathObject subclass that is used like
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
                # convert self.cdlist to a set so its order
                # doesn't matter
                return (self.a == other.a and self.b == other.b and
                        set(self.cdlist) == set(other.cdlist))

            def __hash__(self):
                # reuse tuple's __hash__, but convert cdlist
                # to a frozenset because sets aren't hashable
                return hash((self.a, self.b, frozenset(self.cdlist)))

    ...or like this::

        @derivater.eq_and_hash({'a': None, 'b': None, 'cdlist': frozenset})
        class Toot(derivater.MathObject):

            def __init__(self, a, b, bclist):
                self.a = a
                self.b = b
                self.cdlist = cdlist

    Here ``'a': None, 'b': None`` means that ``a`` and ``b`` will be hashed and
    equal compared as is, and ``cdlist=frozenset`` means that
    ``frozenset(cdlist)`` will be used when hashing and comparing ``cdlist``.
    This means that it doesn't matter which order things are in, but any
    duplicates are ignored.
    """
    def get_stuff(instance):
        result = []
        for attr, converter in sorted(converters.items()):      # sort by keys
            if converter is None:
                converter = (lambda thing: thing)       # noqa
            result.append(converter(getattr(instance, attr)))
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
    """Convert a Python number into a MathObject.

    If *obj* is already a MathObject, it's returned as is.
    """
    if isinstance(obj, MathObject):
        return obj
    if isinstance(obj, int):
        return Integer(obj)
    if isinstance(obj, fractions.Fraction):
        return mathify(obj.numerator) / obj.denominator
    raise TypeError("don't know how to mathify " + repr(obj))


def pythonify(obj):
    """Convert a MathObject into a Python :class:`int` or :class:`fractions.Fr\
action`, but not a float.

    If *obj* is already something that can be passed to :func:`mathify`, it's
    usually returned as is; as an exception, a :class:`fractions.Fraction` that
    represents an integer is returned as an integer directly.
    """
    if isinstance(obj, (int, fractions.Fraction)):
        result = obj
    elif isinstance(obj, Integer):
        result = obj.python_int
    elif isinstance(obj, Add):
        result = sum(map(pythonify, obj.objects))
    elif isinstance(obj, Mul):
        result = 1
        for sub_object in obj.objects:
            result *= pythonify(sub_object)
    elif isinstance(obj, Pow):
        result = (fractions.Fraction(pythonify(obj.base)) **
                  pythonify(obj.exponent))
    else:
        raise TypeError("don't know how to pythonify " + repr(obj))

    if isinstance(result, fractions.Fraction) and result.denominator == 1:
        return result.numerator
    return result


# TODO: the MathObject docstring is not actually used anywhere :(
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

            def __init__(self, numerus):
                self.numerus = mathify(numerus)

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

    def apply_to_content(self, func):
        """Return a new object with *func* applied to every object that this o\
bject contains.

        >>> def two_times(obj):
        ...     return 2*obj
        ...
        >>> (x + y*z).apply_to_content(two_times)
        2*x + 2*y*z

        Override this if your object contains something. For example,
        :class:`.NaturalLog` does something like this::

            def __init__(self, numerus):
                self.numerus = mathify(numerus)

            def apply_to_content(self, func):
                return ln(func(self.numerus))

        By default, this returns *self* unchanged.
        """
        return self

    def apply_recursively(self, func):
        """A recursive version of :func:`apply_to_content`.

        >>> class Lol(MathObject):
        ...     def __init__(self, content):
        ...         self.content = content
        ...     def __repr__(self):
        ...         return 'Lol(%r)' % self.content
        ...
        >>> (x + y*z).apply_recursively(Lol)
        Lol(Lol(x) + Lol(Lol(y)*Lol(z)))

        This function is implemented with :func:`apply_to_content`, so you
        might want to override :func:`apply_to_content` instead if you think
        you need to override this function.
        """
        result = self.apply_to_content(lambda obj: obj.apply_recursively(func))
        return func(result)

    def get_content(self):
        """Return a list of the content that :func:`apply_to_content` applies \
to.

        >>> (x**y).get_content()
        [x, y]

        This is implemented with :func:`apply_to_content`, so usually you don't
        need to override this. Just override :func:`apply_to_content` instead.
        """
        result = []

        def callback(obj):
            result.append(obj)
            return obj

        self.apply_to_content(callback)
        return result

    def add_parenthesize(self):
        return repr(self)

    def mul_parenthesize(self):
        return self.add_parenthesize()

    def pow_parenthesize(self):
        return self.mul_parenthesize()

    def may_depend_on(self, var):
        """Check if this variable depends on the value of *var*.

        The *var* must be a :class:`Symbol`.

        By default, this checks if the content depends on anything using
        :meth:`apply_to_content`, and returns False if there is no content. If
        you think you need to override this, you may want to override
        :meth:`apply_to_content` instead.
        """
        for obj in self.get_content():
            if obj.may_depend_on(var):
                return True
        return False

    def replace(self, old, new):
        """Replace parts of the math object with another.

        >>> ln(2*x).replace(2*x, 3)
        ln(3)
        >>> x.replace(x, y)
        y
        >>> ln(2).replace(x, y)    # nothing happens
        ln(2)

        If you think you want to override this, you may want to override
        :meth:`apply_to_content` instead; this method is implemented with
        :meth:`apply_recursively`, and that uses :meth:`apply_to_content`.
        """
        old = mathify(old)
        new = mathify(new)

        def replacer(obj):
            if obj == old:
                return new
            return obj

        return self.apply_recursively(replacer)

    def with_fraction_coeff(self):
        """Return a ``(fraciton_coefficient, rest)`` tuple.

        >>> (2*x).with_fraction_coeff()
        (2, x)
        >>> (x*y).with_fraction_coeff()
        (1, x*y)
        >>> (2*x/3 + 4*y/5).with_fraction_coeff()
        (2 / 15, 5*x + 6*y)

        The fraction coefficients only consists of :class:`Integers <Integer>`
        that are multiplied or divided together.

        The default implementation returns ``(mathify(1), self)``, and you can
        override this to return something else.
        """
        return (mathify(1), self)

    def derivative(self, wrt):
        """Return the derivative with respect to *wrt*.

        >>> sin(x).derivative(x)
        cos(x)
        >>> sin(y).derivative(x)      # Symbols are independent
        0
        >>> sin(f(x)).derivative(x)   # but SymbolFunctions work better
        cos(f(x))*f'(x)

        The *wrt* must be a :class:`Symbol`.

        If you override this, remember the chain rule! For example,
        :class:`NaturalLog` does something like this...
        ::

            def __init__(self, numerus):
                self.numerus = mathify(numerus)

            def derivative(self, wrt):
                return 1/self.numerus * self.numerus.derivative(wrt)

        ...so we get this:

        >>> ln(x).derivative(x)     # 1/x * x.derivative(x)
        1 / x
        >>> ln(f(x)).derivative(x)  # 1/f(x) * f(x).derivative(x)
        f'(x) / f(x)
        >>> ln(2).derivative(x)     # 1/mathify(2) * mathify(2).derivative(x)
        0
        """
        if not self.may_depend_on(wrt):
            return mathify(0)
        raise TypeError("cannot take derivative of %r with respect to %r"
                        % (self, wrt))

    def gentle_simplify(self):
        """Try to make the object look simpler.

        Usually there's a simple, structury class with a Capitalized name, and
        a convenient constructor function with a lowercase name (often shorter)
        that creates an instance of the class and calls ``gentle_simplify()``.
        Like this::

            class NaturalLog:
                ...

            def ln(x):
                return NaturalLog(x).gentle_simplify()

        This way you can conveniently take a logarithm with :func:`ln`, but if
        you don't want to automagically convert things like ``ln(1)`` into
        ``0``, you can use :class:`NaturalLog` directly.

        >>> ln(1)           # returns mathify(0)
        0
        >>> NaturalLog(1)   # returns a NaturalLog object
        ln(1)
        >>> NaturalLog(1).gentle_simplify()
        0

        Using the ``+``, ``-``, ``*``, ``/`` and ``**`` operators with
        MathObjects calls ``gentle_simplify()`` automagically, so you can e.g.
        do ``obj + 0`` instead of ``obj.gentle_simplify()`` if you like
        obfuscated code. See :ref:`this thing <addmulpow>` if you want to avoid
        automatic ``gentle_simplify()`` calls.
        """
        return self.apply_to_content(operator.methodcaller('gentle_simplify'))

    def simplify(self):
        """Make the object look as simple as possible.

        This is like :meth:`gentle_simplify`, but more aggressive and usually
        not called automatically.
        """
        return self.apply_to_content(operator.methodcaller('simplify'))

    def __add__(self, other):   # self + other
        return Add([self, other]).gentle_simplify()

    __radd__ = __add__          # other + self

    def __neg__(self):          # -self
        return Mul([-1, self]).gentle_simplify()

    def __sub__(self, other):   # self - other
        return self + (-other)

    def __rsub__(self, other):  # other - self
        return other + (-self)

    def __mul__(self, other):   # self * other
        return Mul([self, other]).gentle_simplify()

    __rmul__ = __mul__          # other * self

    def __truediv__(self, other):   # self / other
        # it's important to mathify the -1 because 2**(-1) == 0.5, but
        # we don't want floats
        return self * other**(mathify(-1))

    def __rtruediv__(self, other):  # other / self
        # -1 will be mathified automatically by __pow__
        return other * self**(-1)

    def __pow__(self, other):   # self ** other
        return Pow(self, other).gentle_simplify()

    def __rpow__(self, other):  # other ** self
        return Pow(other, self).gentle_simplify()


@eq_and_hash({'name': None})
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
        self.name = name

    def __repr__(self):
        return self.name

    def may_depend_on(self, other_symbol):
        return (self == other_symbol)

    def derivative(self, wrt):
        if wrt == self:
            return mathify(1)
        return mathify(0)


@eq_and_hash({'name': None, 'arg': None, 'derivative_count': None})
class SymbolFunction(MathObject):
    """Represents an unknown, single-variable function.

    >>> from derivater import SymbolFunction, Symbol
    >>> x = Symbol('x')
    >>> SymbolFunction('f', x)
    f(x)
    >>> SymbolFunction('g', x, derivative_count=2)
    g''(x)

    By default, ``derivater.__main__`` contains functions defined like this::

        from functools import partial
        f = partial(SymbolFunction, 'f')
        g = partial(SymbolFunction, 'g')

    This means that you can type ``f(x)`` to get ``f(x)``.

    >>> f(x)
    f(x)

    There are also ``f_`` and ``g_`` defined like this...
    ::

        f_ = partial(f, derivative_count=1)
        g_ = partial(g, derivative_count=1)

    ...so you can do this:

    >>> f_(x)
    f'(x)

    More derivative examples:

    >>> f(x).derivative(x).derivative(x)
    f''(x)
    >>> f(x).derivative(x).derivative(x).derivative_count
    2
    >>> (f(x) * g(x)).derivative(x)
    f'(x)*g(x) + f(x)*g'(x)
    >>> f(g(x)).derivative(x)
    f'(g(x))*g'(x)
    """

    def __init__(self, name, arg, *, derivative_count=0):
        self.name = name
        self.arg = mathify(arg)
        if derivative_count < 0:
            raise ValueError("negative derivative_count is not supported")
        self.derivative_count = derivative_count

    def __repr__(self):
        return '%s%s(%r)' % (
            self.name, "'" * self.derivative_count, self.arg)

    def apply_to_content(self, func):
        return SymbolFunction(self.name, func(self.arg),
                              derivative_count=self.derivative_count)

    def derivative(self, wrt):
        return (SymbolFunction(self.name, self.arg,
                               derivative_count=self.derivative_count+1)
                * self.arg.derivative(wrt))


@eq_and_hash({'python_int': None})
class Integer(MathObject):
    """An integer with a known value.

    You can create Integer objects yourself or, equivalently, you can pass a
    Python int to :func:`mathify`.

    .. attribute:: python_int

        The equivalent python ``int`` object.
    """

    def __init__(self, python_int):
        if not isinstance(python_int, int):
            if isinstance(python_int, Integer):
                # "cannot create Integer of 2" would be confusing
                raise TypeError("cannot create a new Integer of an Integer")
            raise TypeError("cannot create Integer of " + repr(python_int))
        self.python_int = python_int

    def __repr__(self):
        return str(self.python_int)

    def __float__(self):
        return float(self.python_int)

    def with_fraction_coeff(self):
        return (self, mathify(1))

    def may_depend_on(self, var):   # enough for derivative() to work
        return False

    def add_parenthesize(self):
        if self.python_int < 0:
            return '(' + repr(self) + ')'
        return repr(self)


def _looks_like_negative(expr):
    if isinstance(expr, Mul):
        # len(expr.objects) >= 1 would be more readable in this context, but
        # pep8 **IS** a lawbook.... so..
        return (expr.objects and
                isinstance(expr.objects[0], Integer) and
                expr.objects[0].python_int < 0)
    if isinstance(expr, Integer):
        return expr.python_int < 0
    return False


@eq_and_hash({'objects': frozenset})
class Add(MathObject):
    """An object that represents a bunch of things added together.

    .. attribute:: objects

        List of the added objects.
    """

    def __init__(self, objects):
        self.objects = list(map(mathify, objects))

    def __repr__(self):
        if not self.objects:
            return '0'

        result = [self.objects[0].add_parenthesize()]
        for obj in self.objects[1:]:
            if _looks_like_negative(obj):
                result.append(' - ')
                result.append((-obj).add_parenthesize())
            else:
                result.append(' + ')
                result.append(obj.add_parenthesize())
        return ''.join(result)

    def __float__(self):
        return sum(map(float, self.objects))

    # TODO: how about something like (a+b+c+x).replace(b+c, y)?
    def apply_to_content(self, func):
        return Add(map(func, self.objects))

    def mul_parenthesize(self):
        return '(' + repr(self) + ')'

    # (x + y + z).replace(x + z, a) should be y+a
    def replace(self, old, new):
        old = mathify(old)
        new = mathify(new)

        if isinstance(old, Add):
            if not old.objects:
                raise ValueError(
                    "cannot replace Add([]) by something, maybe use "
                    "gentle_simplify() to turn Add([])'s into zeros?")

            if set(old.objects).issubset(self.objects):
                new_add_objects = self.objects.copy()
                while set(old.objects).issubset(new_add_objects):
                    # put the new object to the last old object's location
                    for obj in old.objects[:-1]:
                        new_add_objects.remove(obj)
                    where = new_add_objects.index(old.objects[-1])
                    new_add_objects[where] = new

                # don't gently_simplify, more useful to see what happens
                return Add(new_add_objects)

        return super().replace(old, new)

    def derivative(self, wrt):
        # d/dx (f(x) + g(x)) = f'(x) + g'(x)
        # also works with more than 2 functions
        return (Add(obj.derivative(wrt) for obj in self.objects)
                .gentle_simplify())

    def with_fraction_coeff(self):
        # reduce() below wants a non-empty sequence but
        # Add([]).with_fraction_coeff() must not error
        if not self.objects:
            return super().with_fraction_coeff()

        coeffs = [
            fractions.Fraction(pythonify(obj.with_fraction_coeff()[0]))
            for obj in self.objects]

        # yes, this handles corner cases
        # sum([]) == 0, (0).denominator == 1
        # fractions.Fraction always moves minuses to numerator, denominator
        # is known to be positive
        the_coeff_bottom = sum(coeffs).denominator
        new_coeffs = [int(coeff*the_coeff_bottom) for coeff in coeffs]
        the_coeff_top = functools.reduce(gcd, new_coeffs)   # gcd of many things

        coeff = mathify(the_coeff_top) / the_coeff_bottom
        return (coeff,
                Add(obj / coeff for obj in self.objects).gentle_simplify())

    def gentle_simplify(self):
        """This override of :meth:`.MathObject.gentle_simplify` does these thi\
ngs:

        * All the added :attr:`objects` are simplified gently.
        * Nested Adds are combined into one; ``Add([a, Add([b, c])])`` becomes
          ``Add([a, b, c])``.
        * Multiplied and divided integers are combined together, and that's
          added to the end of the result.
        * Repeatedly added objects are turned into :class:`Muls <Mul>`;
          ``Add([a, a, b])`` becomes ``Add([2*a, b])``.
        * Integer coefficients are combined: ``Add([2*a, 3*b, 4*a])`` becomes
          ``Add([6*a, 3*b])``.
        * If there's exactly 1 object left, it is returned instead of an Add
          object.
        * If there are no objects left, ``mathify(0)`` is returned instead of
          an Add object.
        """
        flat = []
        for obj in map(operator.methodcaller('gentle_simplify'), self.objects):
            if isinstance(obj, Add):
                flat.extend(obj.objects)
            else:
                flat.append(obj)

        # extract fractions
        frac_value = fractions.Fraction(0)
        no_fracs = []
        for obj in flat:
            if obj.with_fraction_coeff()[1] == mathify(1):
                # purely a fraction, the whole thing is a fraction
                # coefficient of mathify(1)
                frac_value += pythonify(obj)
            else:
                no_fracs.append(obj)

        # turn repeated objects into _Muls
        while max(collections.Counter(no_fracs).values(), default=1) != 1:
            no_fracs = [
                (value * how_many).gentle_simplify()
                for value, how_many in collections.Counter(no_fracs).items()]

        # combine coefficients: 2*x + 3*x becomes 5*x
        # use fractions.Fraction to avoid recursion...
        counts = collections.defaultdict(fractions.Fraction)
        for obj in no_fracs:
            coeff, no_coeff = obj.with_fraction_coeff()
            counts[no_coeff] += pythonify(coeff)

        # should be simple enough by now :D
        parts = [mathify(how_many) * obj for obj, how_many in counts.items()]
        while mathify(0) in parts:
            parts.remove(mathify(0))
        if frac_value != 0:
            parts.append(mathify(frac_value))

        if not parts:
            return mathify(0)
        if len(parts) == 1:
            return parts[0]
        return Add(parts)

    # TODO
    def simplify(self):
        return (Add(part.simplify() for part in self.objects)
                .gentle_simplify())


@eq_and_hash({'objects': frozenset})
class Mul(MathObject):
    """An object that represents a bunch of stuff multiplied with each other.

    .. attribute:: objects

        List of the multiplied objects.
    """

    def __init__(self, objects):
        self.objects = list(map(mathify, objects))

    def __repr__(self):
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
            return '*'.join(obj.mul_parenthesize() for obj in top) or '1'

        # the top uses mul_parenthesize() instead of repr() because otherwise
        # repr((x + y)/z) == 'x + y / z'
        top_string = repr(Mul(top))

        # Mul([Pow(x/y, -2)]) must be represented as 1 / (x**2 / y**2)
        # changing a tiny detail in this breaks some detail in that...
        if len(bottom) == 1:
            bottom_string = (bottom[0].pow_parenthesize()
                             if isinstance(bottom[0], Mul)
                             else bottom[0].mul_parenthesize())
        else:
            bottom_string = Mul(bottom).pow_parenthesize()
        return top_string + ' / ' + bottom_string

    def __float__(self):
        if not self.content:
            return 1.0
        return functools.reduce(operator.mul, map(float, self.content))

    def apply_to_content(self, func):
        return Mul(map(func, self.objects))

    def pow_parenthesize(self):
        return '(' + repr(self) + ')'

    # (x*y*z).replace(x*z, a) should be y*a
    def replace(self, old, new):
        old = mathify(old)
        new = mathify(new)

        if isinstance(old, Mul):
            if not old.objects:
                raise ValueError(
                    "cannot replace Mul([]) by something, maybe use "
                    "gentle_simplify() to turn Mul([])'s into ones?")

            if set(old.objects).issubset(self.objects):
                new_mul_objects = self.objects.copy()
                while set(old.objects).issubset(new_mul_objects):
                    # put the new object to the last old object's location
                    for obj in old.objects[:-1]:
                        new_mul_objects.remove(obj)
                    where = new_mul_objects.index(old.objects[-1])
                    new_mul_objects[where] = new

                # don't gently_simplify, more useful to see what happens
                return Mul(new_mul_objects)

        return super().replace(old, new)

    def derivative(self, wrt):
        # d/dx (f(x)g(x)h(x)) = f'(x)g(x)h(x) + f(x)g'(x)h(x) + f(x)g(x)h'(x)
        # it works like this for more functions
        parts = []
        for i in range(len(self.objects)):      # OMG ITS RANGELEN KITTENS DIE
            parts.append(Mul(self.objects[:i] +
                             [self.objects[i].derivative(wrt)] +
                             self.objects[i+1:]))
        return Add(parts).gentle_simplify()

    # gentle_simplify needs this thing, but with_fraction_coeff() calls
    # gentle_simplify
    def _raw_with_fraction_coeff(self):
        coeff = fractions.Fraction(1)
        result_objects = []

        for obj in self.objects:
            obj_coeff, obj_no_coeff = obj.with_fraction_coeff()
            coeff *= pythonify(obj_coeff)
            result_objects.append(obj_no_coeff)

        return (coeff, result_objects)

    def with_fraction_coeff(self):
        coeff, result_objects = self._raw_with_fraction_coeff()
        return (mathify(coeff), Mul(result_objects).gentle_simplify())

    def gentle_simplify(self):
        """This override of :meth:`.MathObject.gentle_simplify` does these thi\
ngs:

        * All the multiplied :attr:`objects` are simplified gently.
        * Nested Muls are combined into one; ``Mul([a, Mul([b, c])])`` becomes
          ``Mul([a, b, c])``.
        * The coefficient from :meth:`with_fraction_coeff` is moved to
          beginning. If the coefficient is a Mul, two objects are inserted to
          the beginning.
        * Repeatedly added objects are turned into :class:`Pows <Pow>`;
          ``Mul([a, a, b])`` becomes ``Mul([a**2, b])``.
        * Powers with same base are combined: ``Mul([x**a, y, x**b])`` becomes
          ``Mul([x**(a + b), y])``.
        * If there's exactly 1 object left, it is returned instead of a Mul
          object.
        * If there are no objects left, ``mathify(1)`` is returned instead of
          a Mul object.
        """
        flat = []
        for obj in map(operator.methodcaller('gentle_simplify'), self.objects):
            if isinstance(obj, Mul):
                flat.extend(obj.objects)
            elif obj == mathify(0):
                return mathify(0)
            else:
                flat.append(obj)

        # extract the coefficient
        coeff, no_coeff = Mul(flat)._raw_with_fraction_coeff()
        if coeff == 0:
            return mathify(0)

        # not quite sure why, but it recurses if this is moved later :D
        while mathify(1) in no_coeff:
            no_coeff.remove(mathify(1))

        # turn repeated objects into Pows
        while max(collections.Counter(no_coeff).values(), default=1) != 1:
            no_coeff = [
                base ** exponent
                for base, exponent in collections.Counter(no_coeff).items()]

        # combine powers with same bases
        powers = {}     # {base: exponent}
        for obj in no_coeff:
            if isinstance(obj, Pow):
                base = obj.base
                exponent = obj.exponent
            else:
                base = obj
                exponent = mathify(1)
            powers[base] = powers.get(base, mathify(0)) + exponent

        # should be simple enough
        parts = [base ** exponent for base, exponent in powers.items()]
        while mathify(1) in parts:
            parts.remove(mathify(1))

        # look carefully, the numerator ends up there first and
        # fractions.Fraction always brings minus signs to the numerator
        if coeff.denominator != 1:
            parts.insert(0, Pow(coeff.denominator, -1))
        if coeff.numerator != 1:
            parts.insert(0, mathify(coeff.numerator))

        if not parts:
            return mathify(1)
        if len(parts) == 1:
            return parts[0]
        return Mul(parts)

    # TODO
    def simplify(self):
        return Mul(part.simplify() for part in self.objects).gentle_simplify()


@eq_and_hash({'base': None, 'exponent': None})
class Pow(MathObject):
    """An object that represents ``base ** exponent``.

    .. attribute:: base
                   exponent

        Pow objects represent ``base**exponent``.
    """

    def __init__(self, base, exponent):
        self.base = mathify(base)
        self.exponent = mathify(exponent)

    def __repr__(self):
        if self.exponent == mathify(-1):
            # same code as in Mul
            bottom_string = (self.base.pow_parenthesize()
                             if isinstance(self.base, Mul)
                             else self.base.mul_parenthesize())
            return '1 / ' + bottom_string
        return (self.base.pow_parenthesize() + '**' +
                self.exponent.pow_parenthesize())

    def __float__(self):
        # derivater._constants needs this file
        from derivater._constants import e
        if self.base == e:
            # more precision
            return math.exp(float(self.exponent))
        return float(self.base) ** float(self.exponent)

    def pow_parenthesize(self):
        # x**y**z = x**(y**z)
        # that's why (x**y)**z must be shown with parentheses around x**y
        return '(' + repr(self) + ')'

    def apply_to_content(self, func):
        return Pow(func(self.base), func(self.exponent))

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

    def with_fraction_coeff(self):
        if (self.base.with_fraction_coeff()[0] == self.base and
                self.exponent.with_fraction_coeff()[0] == self.exponent):
            return (self, mathify(1))
        return (mathify(1), self)

    def gentle_simplify(self):
        """This override of :meth:`.MathObject.gentle_simplify` does these thi\
ngs:

        * The base and exponent are simplified gently.
        * If the base is also a power, the powers are combined into one;
          ``Pow(Pow(a, b), c)`` becomes ``Pow(a, b*c)``.
        * If the base is a :class:`Mul`, the power is separated into two
          powers; ``Pow(a*b, c)`` becomes ``Pow(a, c) * Pow(b, c)``.
        * If the base and the exponent are 0, this does the same wrongness as
          Python. Try ``0**0`` in a Python interpreter to find out what it is
          and don't blame me for returning a finite value for an indeterminate
          form; blame Python devs instead.
        * If the base is 0, ``mathify(0)`` is returned.
        * If the base is 1, ``mathify(1)`` is returned.
        * If the exponent is 0, ``mathify(1)`` is returned.
        * If the exponent is 1, the base is returned.
        * If the base and exponent are integers such that the whole thing is
          known to be an integer, ``mathify(that integer)`` is returned.
          Currently this does not detect all possible ways to create an
          integer.
        """
        base = self.base.gentle_simplify()
        exponent = self.exponent.gentle_simplify()
        if isinstance(base, Pow):
            # (x**y)**z = x**(y * z)
            return base.base ** (base.exponent * exponent)
        if isinstance(base, Mul):
            return (Mul(obj**self.exponent for obj in base.objects)
                    .gentle_simplify())

        # TODO: buts, e.g. 0**x == 0  but x > 0 ???
        if base == mathify(0) and exponent == mathify(0):
            # python does this wrong, so let's blame it for the result...
            return mathify(0**0)
        if base == mathify(0):
            return mathify(0)
        if base == mathify(1):
            return mathify(1)
        if exponent == mathify(0):
            return mathify(1)
        if exponent == mathify(1):
            return base

        if (isinstance(base, Integer) and isinstance(exponent, Integer) and
                (exponent.python_int >= 0 or base == mathify(-1))):
            # this must be an integer
            # TODO: handle more cases
            return mathify(round(base.python_int ** exponent.python_int))

        return Pow(base, exponent)

    def simplify(self):
        return self.base.simplify() ** self.exponent.simplify()


# TODO: update Pow.__repr__ and maybe Mul.__repr__ to show sqrt( )
def sqrt(x):
    """Return the square root of $x$.

    This is equivalent to ``x**(mathify(1) / 2)``.
    """
    return x**(mathify(1) / 2)
