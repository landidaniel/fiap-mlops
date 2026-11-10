"""Smoke tests do ambiente."""


def test_python_funciona():
    assert 1 + 1 == 2


def test_sklearn_importa():
    import sklearn

    assert sklearn.__version__
