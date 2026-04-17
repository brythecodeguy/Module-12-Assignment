import pytest
import uuid

from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)


def dummy_user_id():
    return uuid.uuid4()


def test_addition_get_result():
    addition = Addition(user_id=dummy_user_id(), a=10, b=5)
    result = addition.get_result()
    assert result == 15


def test_subtraction_get_result():
    subtraction = Subtraction(user_id=dummy_user_id(), a=20, b=5)
    result = subtraction.get_result()
    assert result == 15


def test_multiplication_get_result():
    multiplication = Multiplication(user_id=dummy_user_id(), a=2, b=3)
    result = multiplication.get_result()
    assert result == 6


def test_division_get_result():
    division = Division(user_id=dummy_user_id(), a=100, b=5)
    result = division.get_result()
    assert result == 20


def test_division_by_zero():
    division = Division(user_id=dummy_user_id(), a=50, b=0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        division.get_result()


def test_calculation_factory_addition():
    calc = Calculation.create(
        calculation_type="addition",
        user_id=dummy_user_id(),
        a=1,
        b=2,
    )
    assert isinstance(calc, Addition)
    assert isinstance(calc, Calculation)
    assert calc.get_result() == 3


def test_calculation_factory_subtraction():
    calc = Calculation.create(
        calculation_type="subtraction",
        user_id=dummy_user_id(),
        a=10,
        b=4,
    )
    assert isinstance(calc, Subtraction)
    assert calc.get_result() == 6


def test_calculation_factory_multiplication():
    calc = Calculation.create(
        calculation_type="multiplication",
        user_id=dummy_user_id(),
        a=3,
        b=4,
    )
    assert isinstance(calc, Multiplication)
    assert calc.get_result() == 12


def test_calculation_factory_division():
    calc = Calculation.create(
        calculation_type="division",
        user_id=dummy_user_id(),
        a=100,
        b=5,
    )
    assert isinstance(calc, Division)
    assert calc.get_result() == 20


def test_calculation_factory_invalid_type():
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create(
            calculation_type="modulus",
            user_id=dummy_user_id(),
            a=10,
            b=3,
        )


def test_calculation_factory_case_insensitive():
    for calc_type in ["addition", "Addition", "ADDITION", "AdDiTiOn"]:
        calc = Calculation.create(
            calculation_type=calc_type,
            user_id=dummy_user_id(),
            a=5,
            b=3,
        )
        assert isinstance(calc, Addition)
        assert calc.get_result() == 8


def test_polymorphic_list_of_calculations():
    user_id = dummy_user_id()

    calculations = [
        Calculation.create("addition", user_id, 1, 2),
        Calculation.create("subtraction", user_id, 10, 3),
        Calculation.create("multiplication", user_id, 2, 4),
        Calculation.create("division", user_id, 100, 5),
    ]

    assert isinstance(calculations[0], Addition)
    assert isinstance(calculations[1], Subtraction)
    assert isinstance(calculations[2], Multiplication)
    assert isinstance(calculations[3], Division)

    results = [calc.get_result() for calc in calculations]
    assert results == [3, 7, 8, 20]


def test_polymorphic_method_calling():
    user_id = dummy_user_id()

    calc_types = ["addition", "subtraction", "multiplication", "division"]
    expected_results = [12, 8, 20, 5]

    for calc_type, expected in zip(calc_types, expected_results):
        calc = Calculation.create(calc_type, user_id, 10, 2)
        result = calc.get_result()
        assert result == expected


def test_base_calculation_get_result_raises_not_implemented():
    calc = Calculation(user_id=dummy_user_id(), type="calculation", a=1, b=2)
    with pytest.raises(NotImplementedError, match="Subclasses must implement get_result"):
        calc.get_result()


def test_calculation_repr_contains_type_a_and_b():
    calc = Addition(
        user_id=dummy_user_id(),
        type="addition",
        a=1,
        b=2,
        result=3
    )
    text = repr(calc)
    assert "addition" in text
    assert "a=1" in text
    assert "b=2" in text