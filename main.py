# main.py

from uuid import UUID

import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.calculation import Calculation
from app.models.user import User
from app.operations import add, subtract, multiply, divide
from app.schemas.calculation import CalculationCreate, CalculationRead, CalculationUpdate
from app.schemas.user import UserRead, Token
from app.schemas.base import UserCreate

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/health")
async def health():
    return {"status": "ok"}


# -----------------------------
# Existing calculator schemas
# -----------------------------
class OperationRequest(BaseModel):
    a: float = Field(..., description="The first number")
    b: float = Field(..., description="The second number")

    @field_validator("a", "b")
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Both a and b must be numbers.")
        return value


class OperationResponse(BaseModel):
    result: float = Field(..., description="The result of the operation")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")


# -----------------------------
# Exception handlers
# -----------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    logger.error(f"ValidationError on {request.url.path}: {error_messages}")
    return JSONResponse(
        status_code=400,
        content={"error": error_messages},
    )


# -----------------------------
# Existing routes
# -----------------------------
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/add", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def add_route(operation: OperationRequest):
    try:
        result = add(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Add Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/subtract", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def subtract_route(operation: OperationRequest):
    try:
        result = subtract(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Subtract Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/multiply", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def multiply_route(operation: OperationRequest):
    try:
        result = multiply(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Multiply Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/divide", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def divide_route(operation: OperationRequest):
    try:
        result = divide(operation.a, operation.b)
        return OperationResponse(result=result)
    except ValueError as e:
        logger.error(f"Divide Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Divide Operation Internal Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# -----------------------------
# User routes
# -----------------------------
@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["users"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = User.register(db, user.model_dump())
        db.commit()
        db.refresh(new_user)
        return UserRead.model_validate(new_user)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Register error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/users/login", response_model=Token, tags=["users"])
def login_user(user_login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token_data = User.authenticate(db, user_login.username, user_login.password)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


# -----------------------------
# Calculation routes
# -----------------------------
@app.post("/calculations", response_model=CalculationRead, status_code=status.HTTP_201_CREATED, tags=["calculations"])
def create_calculation(
    calculation: CalculationCreate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user),
):
    try:
        new_calculation = Calculation.create(
            calculation_type=calculation.type,
            user_id=current_user.id,
            a=calculation.a,
            b=calculation.b,
        )
        db.add(new_calculation)
        db.commit()
        db.refresh(new_calculation)
        return CalculationRead.model_validate(new_calculation)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Create calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/calculations", response_model=list[CalculationRead], tags=["calculations"])
def browse_calculations(
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user),
):
    calculations = (
        db.query(Calculation)
        .filter(Calculation.user_id == current_user.id)
        .order_by(Calculation.created_at.desc())
        .all()
    )
    return [CalculationRead.model_validate(calc) for calc in calculations]


@app.get("/calculations/{calculation_id}", response_model=CalculationRead, tags=["calculations"])
def read_calculation(
    calculation_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user),
):
    calculation = (
        db.query(Calculation)
        .filter(
            Calculation.id == calculation_id,
            Calculation.user_id == current_user.id,
        )
        .first()
    )

    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")

    return CalculationRead.model_validate(calculation)


@app.put("/calculations/{calculation_id}", response_model=CalculationRead, tags=["calculations"])
def update_calculation(
    calculation_id: UUID,
    calculation_update: CalculationUpdate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user),
):
    calculation = (
        db.query(Calculation)
        .filter(
            Calculation.id == calculation_id,
            Calculation.user_id == current_user.id,
        )
        .first()
    )

    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")

    update_data = calculation_update.model_dump(exclude_unset=True)

    new_type = update_data.get("type", calculation.type)
    new_a = update_data.get("a", calculation.a)
    new_b = update_data.get("b", calculation.b)

    try:
        updated_calc = Calculation.create(
            calculation_type=new_type,
            user_id=current_user.id,
            a=new_a,
            b=new_b,
        )

        calculation.type = updated_calc.type
        calculation.a = updated_calc.a
        calculation.b = updated_calc.b
        calculation.result = updated_calc.result

        db.commit()
        db.refresh(calculation)
        return CalculationRead.model_validate(calculation)

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Update calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/calculations/{calculation_id}", status_code=204, tags=["calculations"])
def delete_calculation(
    calculation_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user),
):
    calculation = (
        db.query(Calculation)
        .filter(
            Calculation.id == calculation_id,
            Calculation.user_id == current_user.id,
        )
        .first()
    )

    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")

    db.delete(calculation)
    db.commit()
    return None


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)