from derivater._base import MathObject


# __eq__ and __hash__ check "a is b" by default, that's good
class NamedConstant(MathObject):

    def __init__(self, name):
        if not isinstance(name, str):
            raise TypeError("invalid constant name " + repr(name))
        self.name = name

    def __repr__(self):
        return self.name

    def may_depend_on(self, var):   # enough for derivative() to work
        return False


e = NamedConstant('e')
tau = NamedConstant('tau')
pi = tau/2
