import minitorch
import pytest
from hypothesis import given
from .strategies import tensors, shaped_tensors
from minitorch import assert_close


# TESTS are the same as test_tensor with different backend
CudaTensorFunctions = minitorch.make_tensor_functions(minitorch.CudaOps)

v = 4.524423
one_arg = [
    ("neg", lambda a: -a),
    ("addconstant", lambda a: a + v),
    ("lt", lambda a: a < v),
    ("subconstant", lambda a: a - v),
    ("mult", lambda a: 5 * a),
    ("div", lambda a: a / v),
    ("sig", lambda a: a.sigmoid()),
    ("log", lambda a: (a + 100000).log()),
    ("relu", lambda a: (a + 2).relu()),
]

reduce = [
    ("sum", lambda a: a.sum()),
    ("sum2", lambda a: a.sum(0)),
]
two_arg = [("add", lambda a, b: a + b), ("mul", lambda a, b: a * b)]


@given(tensors(backend=CudaTensorFunctions))
@pytest.mark.task3_3
@pytest.mark.parametrize("fn", one_arg)
def test_one_args(fn, t1):
    t2 = fn[1](t1)
    for ind in t2._tensor.indices():
        assert_close(t2[ind], fn[1](minitorch.Scalar(t1[ind])).data)


@given(shaped_tensors(2, backend=CudaTensorFunctions))
@pytest.mark.task3_3
@pytest.mark.parametrize("fn", two_arg)
def test_two_args(fn, ts):
    t1, t2 = ts
    t3 = fn[1](t1, t2)
    for ind in t3._tensor.indices():
        assert (
            t3[ind] == fn[1](minitorch.Scalar(t1[ind]), minitorch.Scalar(t2[ind])).data
        )


@given(tensors(backend=CudaTensorFunctions))
@pytest.mark.task3_3
@pytest.mark.parametrize("fn", one_arg)
def test_one_derivative(fn, t1):
    minitorch.grad_check(fn[1], t1)


@given(tensors(backend=CudaTensorFunctions))
@pytest.mark.task3_3
@pytest.mark.parametrize("fn", reduce)
def test_reduce(fn, t1):
    minitorch.grad_check(fn[1], t1)


@given(shaped_tensors(2, backend=CudaTensorFunctions))
@pytest.mark.task3_3
@pytest.mark.parametrize("fn", two_arg)
def test_two_grad(fn, ts):
    t1, t2 = ts
    minitorch.grad_check(fn[1], t1, t2)


@given(shaped_tensors(2, backend=CudaTensorFunctions))
@pytest.mark.task3_3
@pytest.mark.parametrize("fn", two_arg)
def test_two_grad_broadcast(fn, ts):
    t1, t2 = ts
    minitorch.grad_check(fn[1], t1, t2)

    # broadcast check
    minitorch.grad_check(fn[1], t1.sum(0), t2)
    minitorch.grad_check(fn[1], t1, t2.sum(0))
