import pytest
from app import calculate
def test_addition():
    assert calculate(2, 3, "add") == 5

def test_subtraction():
    assert calculate(5, 2, "subtract") == 3

def test_division_by_zero():
    with pytest.raises(ValueError):
        calculate(10, 0, "divide")

def test_unknown_operation():
    with pytest.raises(ValueError):
        calculate(1, 2, "power")
