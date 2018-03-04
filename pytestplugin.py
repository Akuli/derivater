# this is here because anything in tests/ doesn't affect tests in docs/
# https://github.com/pytest-dev/pytest/issues/2379
import pytest

import derivater.__main__ as handies


@pytest.fixture(autouse=True)
def add_handy_stuff(doctest_namespace):
    for name in dir(handies):
        if not name.startswith('_'):
            doctest_namespace[name] = getattr(handies, name)


# equality checker for mathy objects
@pytest.fixture
def hasheq():
    return (lambda a, b: (a == b and hash(a) == hash(b)))
