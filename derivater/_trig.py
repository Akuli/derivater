import functools

from derivater._base import MathObject, eq_and_hash, mathify, sqrt


def trig_func_class(repr_name):
    def result(klass):
        def init(self, arg):
            self.arg = mathify(arg)

        def apply_to_content(self, func):
            return klass(func(self.arg))

        klass.__init__ = init
        klass.__repr__ = lambda self: '%s(%r)' % (repr_name, self.arg)
        klass.apply_to_content = apply_to_content
        klass.pow_parenthesize = lambda self: '(' + repr(self) + ')'
        return eq_and_hash({'arg': None})(klass)

    return result


@trig_func_class('sin')
class Sine(MathObject):

    def derivative(self, wrt):
        return cos(self.arg) * self.arg.derivative(wrt)

    def _reduce_angle_2(self):
        return 2*sin(self.arg/2)*cos(self.arg/2)

    def _reduce_angle_3(self):
        return 3*sin(self.arg/3) - 4*sin(self.arg/3)**3


@trig_func_class('cos')
class Cosine(MathObject):

    def derivative(self, wrt):
        return -sin(self.arg) * self.arg.derivative(wrt)

    def _reduce_angle_2(self):
        return cos(self.arg/2)**2 - sin(self.arg/2)**2

    def _reduce_angle_3(self):
        return 4*cos(self.arg/3)**3 - 3*cos(self.arg/3)


@trig_func_class('tan')
class Tangent(MathObject):

    def derivative(self, wrt):
        # (sin(x) / cos(x)).derivative(x) returns (sin(x))**2/(cos(x))**2 + 1
        # i want to replace sin(x) / cos(x) with tan(x), but Mul.rewrite()
        # doesn't handle that too well yet :(
        # cos(x) = sin(x) / (sin(x) / cos(x)) = sin(x) / tan(x)
        return ((sin(self.arg) / cos(self.arg))
                .derivative(wrt)
                .replace(cos(self.arg), sin(self.arg)/tan(self.arg))
                .gentle_simplify())


@trig_func_class('asin')
class ArcSine(MathObject):

    def derivative(self, wrt):
        return 1/sqrt(1 - self.arg**2) * self.arg.derivative(wrt)


@trig_func_class('acos')
class ArcCosine(MathObject):

    def derivative(self, wrt):
        return -1/sqrt(1 - self.arg**2) * self.arg.derivative(wrt)


@trig_func_class('atan')
class ArcTangent(MathObject):

    def derivative(self, wrt):
        return 1/(1 + self.arg**2) * self.arg.derivative(wrt)


def sin(x): return Sine(x).gentle_simplify()            # noqa
def cos(x): return Cosine(x).gentle_simplify()          # noqa
def tan(x): return Tangent(x).gentle_simplify()         # noqa
def asin(x): return ArcSine(x).gentle_simplify()        # noqa
def acos(x): return ArcCosine(x).gentle_simplify()      # noqa
def atan(x): return ArcTangent(x).gentle_simplify()     # noqa

def sec(x): return 1/cos(x)         # noqa
def csc(x): return 1/sin(x)         # noqa
def cot(x): return cos(x)/sin(x)    # noqa
def asec(x): return asin(1/x)       # noqa
def acsc(x): return acos(1/x)       # noqa
def acot(x): return atan(1/x)       # noqa


def _reduce_angles(ratio, big_trig_arg, obj):
    if isinstance(obj, (Sine, Cosine)) and obj.arg == big_trig_arg:
        return getattr(obj, '_reduce_angle_' + str(ratio))()
    return obj


def trig_simplify(obj):
    trig_args = set()

    def to_sincos(sub_object):
        # TODO: do something with inverse trig functions
        if isinstance(sub_object, (Sine, Cosine, Tangent)):
            trig_args.add(sub_object.arg)
        if isinstance(sub_object, Tangent):
            return sin(sub_object.arg) / cos(sub_object.arg)
        return sub_object

    obj = obj.simplify().apply_recursively(to_sincos).simplify()

    # which angles should be reduced?
    for smaller in trig_args:
        for bigger in (trig_args - {smaller}):
            ratio = (bigger / smaller).simplify()
            if ratio in {mathify(2), mathify(3)}:
                callback = functools.partial(_reduce_angles, ratio, bigger)
                obj = obj.apply_recursively(callback).simplify()

    while True:
        old_obj = obj
        for arg in trig_args:
            obj = obj.replace(tan(arg), sin(arg) / cos(arg)).simplify()

            # TODO: do something with inverse_trig_args

            # Pythagorean identity
            obj = obj.replace(sin(arg)**2 + cos(arg)**2, 1).simplify()
            obj = obj.replace(1 - sin(arg)**2, cos(arg)**2).simplify()
            obj = obj.replace(1 - cos(arg)**2, sin(arg)**2).simplify()

        if obj == old_obj:
            # nothing simplifies anymore, we're done
            break

    for arg in trig_args:
        obj = obj.replace(sin(arg) / cos(arg), tan(arg))
    return obj
