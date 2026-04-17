# Module 11

## Module Overview

This module builds on the FastAPI application by adding a polymorphic calculation system with full testing coverage. The goal was to understand how object oriented design, database models, and testing all connect in a backend system.

---

## Docker Setup

Start the application:

```bash
docker compose up --build
```

This starts:

- FastAPI application  
- PostgreSQL database  
- pgAdmin interface  

---

## Docker Hub Repository

<https://hub.docker.com/r/bry633/module-11-assignment>

---

## Access Application

FastAPI:  
<http://localhost:8000>  

pgAdmin:  
<http://localhost:5050>  

Login:

- Email: <admin@example.com>  
- Password: admin  

---

## Database Connection

- Host: db  
- Username: postgres  
- Password: postgres  
- Database: fastapi_db  

---

## Authentication Features

JWT-based authentication is implemented.

### User Registration

Users register with:

- first name  
- last name  
- email  
- username  
- password  

Passwords are securely hashed using bcrypt.

### User Login

- Login with username or email  
- JWT token returned on success  
- Token required for protected routes  

---

## Calculation System

This module introduces a polymorphic calculation system using SQLAlchemy.

### Supported Operations

- Addition  
- Subtraction  
- Multiplication  
- Division  

### Key Features

- Polymorphism using SQLAlchemy inheritance  
- Factory pattern using `Calculation.create()`  
- Dynamic creation of calculation types  
- Input validation (at least two numbers required)  
- Error handling (e.g., division by zero)  

Example:

```python
calc = Calculation.create("addition", user_id, [1, 2, 3])
result = calc.get_result()  # 6
```

---

## API Operations

### Create User

- Handles user registration  

### Authenticate User

- Verifies credentials  
- Updates last login  
- Returns JWT token  

### Protected Routes

- Requires valid JWT  
- Ensures user-specific access  

### Calculations

- Create and compute calculations  
- Results stored and linked to users  

---

## Testing

Run tests:

```bash
pytest -q
```

Includes:

- Unit tests  
- Integration tests  
- Calculation factory tests  
- Polymorphism tests  
- Edge case handling  

Results:

- 100% test coverage  
- All tests passing  

---

## CI/CD Pipeline

GitHub Actions automates:

1. Run Tests  
2. Security Scan (Trivy)  
3. Build and Push Docker Image  

---

## Docker Image

Includes:

- FastAPI app  
- Secure dependencies  
- PostgreSQL integration  

---

## Security

- Password hashing with bcrypt  
- JWT authentication  
- Dependency updates  
- Trivy vulnerability scanning  

---

## Documentation

- [Module11_Screenshots.pdf](./Module11_Screenshots.pdf) – GitHub Actions and Docker Hub Screenshots
- [Module11_Reflection.pdf](./Module11_Reflection.pdf) – Reflection  

---
