# 1. Authentication Guide

## Overview
This guide covers user authentication, registration, login, and password reset functionality.

## 📋 Prerequisites
- Django server running
- Access to Swagger UI or API client (Postman/Insomnia)

---

## Step 1: Send Verification Code

**Purpose**: Send a 6-digit verification code to a phone number for login/registration.

**Endpoint**: `POST /api/v1/auth/send-code/`

**Headers**: None (public endpoint)

**Request Body**:
```json
{
  "phone_number": "+989121234567"
}
```

**Response** (200 OK):
```json
{
  "message": "Verification code sent successfully",
  "code": "123456"
}
```
> **Note**: In production, the code won't be returned. Check SMS service.

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/send-code/" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+989121234567"}'
```

---

## Step 2: Verify Code

**Purpose**: Verify the code sent to phone number (prepares for login/registration).

**⚠️ Important Note**: This endpoint **ONLY validates** the code. It does NOT log you in or create a user. For actual authentication, use the `/login/` or `/register/` endpoints after verification.

**Endpoint**: `POST /api/v1/auth/verify-code/`

**Headers**: None (public endpoint)

**Request Body**:
```json
{
  "phone_number": "+989121234567",
  "code": "123456"
}
```

**Response** (200 OK):
```json
{
  "message": "Code verified successfully"
}
```

**Response** (400 Bad Request):
```json
{
  "error": "Invalid or expired code"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/verify-code/" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+989121234567", "code": "123456"}'
```

---

## Step 3: Register New User

**Purpose**: Register a new user account with phone verification.

**Endpoint**: `POST /api/v1/auth/register/`

**Headers**: None (public endpoint)

**Request Body**:
```json
{
  "phone_number": "+989121234567",
  "code": "123456",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com"
}
```

**Minimal Request** (only required fields):
```json
{
  "phone_number": "+989121234567",
  "code": "123456"
}
```

**Response** (201 Created):
```json
{
  "token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
  "user": {
    "id": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "phone_number": "+989121234567",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "email_confirmed": true
  },
  "message": "Registration successful"
}
```

**Response** (400 Bad Request - User exists):
```json
{
  "error": "User with this phone number already exists"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+989121234567",
    "code": "123456",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com"
  }'
```

**💡 Save the `token` from response** - you'll need it for all authenticated requests!

---

## Step 4: Login

**Purpose**: Login with existing phone number and verification code.

**Endpoint**: `POST /api/v1/auth/login/`

**Headers**: None (public endpoint)

**Request Body**:
```json
{
  "phone_number": "+989121234567",
  "code": "123456"
}
```

**Response** (200 OK):
```json
{
  "token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
  "user": {
    "id": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "phone_number": "+989121234567",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "email_confirmed": true
  },
  "message": "Login successful"
}
```

**Response** (400 Bad Request):
```json
{
  "error": "Invalid or expired code"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+989121234567", "code": "123456"}'
```

**💡 Save the `token` from response!**

---

## Step 5: Logout

**Purpose**: Logout the current user (invalidates token).

**Endpoint**: `POST /api/v1/auth/logout/`

**Headers**:
```
Authorization: Token abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "message": "Logout successful"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/logout/" \
  -H "Authorization: Token abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
```

---

## Step 6: Forgot Password

**Purpose**: Request password reset code.

**Endpoint**: `POST /api/v1/auth/forgot-password/`

**Headers**: None (public endpoint)

**Request Body**:
```json
{
  "phone_number": "+989121234567"
}
```

**Response** (200 OK):
```json
{
  "message": "Password reset code sent successfully"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/forgot-password/" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+989121234567"}'
```

---

## Step 7: Reset Password

**Purpose**: Reset password using verification code.

**Endpoint**: `POST /api/v1/auth/reset-password/`

**Headers**: None (public endpoint)

**Request Body**:
```json
{
  "phone_number": "+989121234567",
  "code": "123456",
  "new_password": "NewSecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "message": "Password reset successfully"
}
```

**Response** (400 Bad Request):
```json
{
  "error": "Invalid or expired code"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/reset-password/" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+989121234567",
    "code": "123456",
    "new_password": "NewSecurePassword123!"
  }'
```

---

## ✅ Testing Checklist

- [ ] Send verification code
- [ ] Verify code received
- [ ] Register new user
- [ ] Login with existing user
- [ ] Logout
- [ ] Forgot password flow
- [ ] Reset password

---

## 🔑 Authentication Token Usage

After login/registration, use the token in all subsequent requests:

**Header Format**:
```
Authorization: Token your-token-here
```

**Example**:
```
Authorization: Token abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

---

## ⚠️ Common Errors

1. **Invalid code**: Code expired (5 minutes) or already used
   - Solution: Request a new code

2. **User already exists**: Phone number already registered
   - Solution: Use login instead of register

3. **Missing token**: Forgot to include Authorization header
   - Solution: Add `Authorization: Token <your-token>` header

---

**Next Step**: [2-user-profile-guide](../2-user-profile-guide/README.md)

