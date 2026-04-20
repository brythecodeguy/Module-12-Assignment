# Module 12

## Module Overview

This module extends the FastAPI application by implementing a fully secured API with authentication, database integration, Docker deployment, and complete test coverage.

The system allows users to register, authenticate, and perform calculations that are stored and retrieved from a PostgreSQL database. All protected routes require authentication using JWT tokens via OAuth2.

---

## Docker Setup

The FastAPI application runs using Uvicorn inside the container:
uvicorn app.main:app --host 0.0.0.0 --port 8000

To Start the application:

```bash
docker compose up --build
```

This starts:

- FastAPI application  
- PostgreSQL database  
- pgAdmin interface  

---

## Docker Hub Repository

<https://hub.docker.com/r/bry633/module-12-assignment>

---

## Access Application

FastAPI (Swagger UI):  
<http://localhost:8000/docs>  

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

## Authentication System

JWT-based authentication is implemented using OAuth2 Password Flow.

### User Registration

Users register with:

- first_name  
- last_name  
- email  
- username  
- password  
- confirm_password  

Passwords are securely hashed using bcrypt.

---

### User Login

- Login with username and password  
- Returns:
  - access_token  
  - refresh_token  
- Token is required for protected endpoints  

---

### Authorization (Swagger UI)

1. Register a user  
2. Login to receive credentials  
3. Click **Authorize** in Swagger  
4. Enter username + password  
5. Swagger automatically attaches JWT token  

---

## Protected API Endpoints

All calculation endpoints require authentication.

### Create Calculation

POST `/calculations`

Example:

{
  "a": 10,
  "b": 5,
  "type": "addition"
}

Response:

{
  "result": 15
}

---

### Get Calculations

GET `/calculations`

Returns all calculations for the authenticated user.

---

## Calculation System

Supports the following operations:

- Addition  
- Subtraction  
- Multiplication  
- Division  

### Features

- Input validation  
- Error handling (e.g., division by zero)  
- User-specific data storage  
- Results persisted in database  

---

## Testing

Run tests:

pytest --run-slow --cov=app --cov-fail-under=100

Includes:

- Unit tests  
- Integration tests  
- API endpoint tests  
- Authentication tests  
- Database tests  

Results:

- 189 tests passing  
- 100% code coverage  

---

## CI/CD Pipeline

GitHub Actions pipeline includes:

1. Run tests  
2. Enforce 100% coverage  
3. Security scan using Trivy  
4. Build Docker image  
5. Push to Docker Hub  

---

## Security

- Password hashing with bcrypt  
- JWT authentication  
- OAuth2 password flow  
- Protected API routes  
- Dependency vulnerability scanning (Trivy)  
- Fixed critical vulnerability:
  - python-multipart upgraded to secure version  

---

## Docker Image

Includes:

- FastAPI application  
- PostgreSQL database integration  
- Secure dependencies  
- Production-ready configuration  

---

## Screenshots

Include the following in your submission:

- [Module12_Screenshots.pdf](./Module12_Screenshots.pdf) – Screnshots of GitHub Actions and demonstration of user registration/login and operational calculation endpoints

1. User registration (POST /users/register)  
2. User login with token response  
3. Swagger Authorize dialog  
4. Create calculation request/response  
5. Get calculations response  
6. GitHub Actions passing  

---

## Reflection

Reflection on experience with this module:

- [Module12_Reflection.pdf](./Module12_Reflection.pdf) – Reflection  

The project integrates all major backend concepts into a working, production-style application.
