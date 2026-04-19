import pytest
from uuid import uuid4
from datetime import datetime
from pydantic import ValidationError

from app.schemas.calculation import (
    CalculationType,
    CalculationBase,
    CalculationCreate,
    CalculationUpdate,
    CalculationRead,
)


def test_calculation_type_enum_values():
    assert CalculationType.ADDITION.value == "addition"
    assert CalculationType.SUBTRACTION.value == "subtraction"
    assert CalculationType.MULTIPLICATION.value == "multiplication"
    assert CalculationType.DIVISION.value == "division"


def test_calculation_base_valid_addition():
    data = {
        "type": "addition",
        "a": 10.5,
        "b": 3,
    }
    calc = CalculationBase(**data)
    assert calc.type == CalculationType.ADDITION
    assert calc.a == 10.5
    assert calc.b == 3


def test_calculation_base_valid_subtraction():
    data = {
        "type": "subtraction",
        "a": 20,
        "b": 5.5,
    }
    calc = CalculationBase(**data)
    assert calc.type == CalculationType.SUBTRACTION
    assert calc.a == 20
    assert calc.b == 5.5


def test_calculation_base_case_insensitive_type():
    for type_variant in ["Addition", "ADDITION", "AdDiTiOn"]:
        data = {"type": type_variant, "a": 1, "b": 2}
        calc = CalculationBase(**data)
        assert calc.type == CalculationType.ADDITION


def test_calculation_base_invalid_type():
    data = {
        "type": "modulus",
        "a": 10,
        "b": 3,
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationBase(**data)

    assert "Calculation type must be one of" in str(exc_info.value)


def test_calculation_base_division_by_zero():
    data = {
        "type": "division",
        "a": 100,
        "b": 0,
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationBase(**data)

    assert "Division by zero is not allowed" in str(exc_info.value)


def test_calculation_base_zero_numerator_ok():
    data = {
        "type": "division",
        "a": 0,
        "b": 5,
    }
    calc = CalculationBase(**data)
    assert calc.a == 0
    assert calc.b == 5


def test_calculation_create_valid():
    data = {
        "type": "multiplication",
        "a": 2,
        "b": 3,
    }
    calc = CalculationCreate(**data)
    assert calc.type == CalculationType.MULTIPLICATION
    assert calc.a == 2
    assert calc.b == 3


def test_calculation_create_missing_type():
    data = {
        "a": 1,
        "b": 2,
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)

    assert "type" in str(exc_info.value)


def test_calculation_create_missing_a():
    data = {
        "type": "addition",
        "b": 2,
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)

    assert "a" in str(exc_info.value)


def test_calculation_create_missing_b():
    data = {
        "type": "addition",
        "a": 1,
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(**data)

    assert "b" in str(exc_info.value)


def test_calculation_update_valid():
    data = {
        "a": 42,
        "b": 7,
    }
    calc = CalculationUpdate(**data)
    assert calc.a == 42
    assert calc.b == 7


def test_calculation_update_all_fields_optional():
    data = {}
    calc = CalculationUpdate(**data)
    assert calc.a is None
    assert calc.b is None
    assert calc.type is None


def test_calculation_update_division_by_zero():
    data = {
        "type": "division",
        "a": 10,
        "b": 0,
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationUpdate(**data)

    assert "Division by zero is not allowed" in str(exc_info.value)


def test_calculation_read_valid():
    data = {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "type": "addition",
        "a": 10,
        "b": 5,
        "result": 15.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    calc = CalculationRead(**data)
    assert calc.result == 15.0
    assert calc.type == CalculationType.ADDITION


def test_calculation_read_missing_result():
    data = {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "type": "multiplication",
        "a": 2,
        "b": 3,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationRead(**data)

    assert "result" in str(exc_info.value)


def test_multiple_calculations_with_different_types():
    calcs_data = [
        {"type": "addition", "a": 1, "b": 2},
        {"type": "subtraction", "a": 10, "b": 3},
        {"type": "multiplication", "a": 2, "b": 4},
        {"type": "division", "a": 100, "b": 5},
    ]

    calcs = [CalculationCreate(**data) for data in calcs_data]

    assert len(calcs) == 4
    assert calcs[0].type == CalculationType.ADDITION
    assert calcs[1].type == CalculationType.SUBTRACTION
    assert calcs[2].type == CalculationType.MULTIPLICATION
    assert calcs[3].type == CalculationType.DIVISION


def test_schema_with_large_numbers():
    data = {
        "type": "multiplication",
        "a": 1e10,
        "b": 1e10,
    }
    calc = CalculationBase(**data)
    assert isinstance(calc.a, float)
    assert isinstance(calc.b, float)


def test_schema_with_negative_numbers():
    data = {
        "type": "addition",
        "a": -5,
        "b": -10,
    }
    calc = CalculationBase(**data)
    assert calc.a == -5
    assert calc.b == -10


def test_schema_with_mixed_int_and_float():
    data = {
        "type": "subtraction",
        "a": 100,
        "b": 23.5,
    }
    calc = CalculationBase(**data)
    assert calc.a == 100
    assert calc.b == 23.5


def test_calculation_base_model_validator_raises_for_division_by_zero():
    calc = CalculationBase.model_construct(
        type=CalculationType.DIVISION,
        a=10,
        b=0,
    )

    with pytest.raises(ValueError, match="Division by zero is not allowed"):
        calc.validate_inputs()


def test_calculation_update_model_validator_raises_for_division_by_zero():
    calc = CalculationUpdate.model_construct(
        type=CalculationType.DIVISION,
        a=10,
        b=0,
    )

    with pytest.raises(ValueError, match="Division by zero is not allowed"):
        calc.validate_inputs()