from enum import Enum
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator


class CalculationType(str, Enum):
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"


class CalculationBase(BaseModel):
    type: CalculationType = Field(
        ...,
        description="Operation to perform",
        examples=["addition"]
    )
    a: float = Field(
        ...,
        description="First number used in the calculation",
        examples=[8]
    )
    b: float = Field(
        ...,
        description="Second number used in the calculation",
        examples=[2]
    )

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value):
        valid_types = {item.value for item in CalculationType}
        if not isinstance(value, str) or value.lower() not in valid_types:
            raise ValueError(
                f"Calculation type must be one of: {', '.join(sorted(valid_types))}"
            )
        return value.lower()

    @model_validator(mode="after")
    def validate_inputs(self):
        if self.type == CalculationType.DIVISION and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"type": "addition", "a": 8, "b": 2},
                {"type": "division", "a": 20, "b": 5}
            ]
        }
    )


class CalculationCreate(CalculationBase):
    user_id: UUID = Field(
        ...,
        description="User ID linked to this calculation",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "multiplication",
                "a": 4,
                "b": 3,
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class CalculationUpdate(BaseModel):
    a: Optional[float] = Field(
        None,
        description="Updated first number",
        examples=[12]
    )
    b: Optional[float] = Field(
        None,
        description="Updated second number",
        examples=[4]
    )
    type: Optional[CalculationType] = Field(
        None,
        description="Updated calculation type",
        examples=["addition"]
    )

    @model_validator(mode="after")
    def validate_inputs(self):
        if self.type == CalculationType.DIVISION and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "a": 12,
                "b": 4
            }
        }
    )


class CalculationRead(CalculationBase):
    id: UUID = Field(
        ...,
        description="Unique identifier for the calculation",
        examples=["123e4567-e89b-12d3-a456-426614174999"]
    )
    user_id: UUID = Field(
        ...,
        description="User ID associated with this calculation",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    created_at: datetime = Field(
        ...,
        description="Date and time the calculation was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Date and time the calculation was last updated"
    )
    result: float = Field(
        ...,
        description="Calculated output",
        examples=[24.0]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174999",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "multiplication",
                "a": 4,
                "b": 3,
                "result": 12.0,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }
    )