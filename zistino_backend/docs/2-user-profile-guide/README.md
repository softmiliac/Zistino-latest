# 2. User Profile Guide

## Overview
This guide covers user profile management, addresses, and vehicle information. **Endpoints are organized by priority: Read first, then Create.**

## 📋 Prerequisites
- Completed [1-authentication-guide](../1-authentication-guide/README.md)
- Have a valid authentication token

---

## 📖 READING PROFILE DATA (Priority 1)

### Step 1: Get User Profile

**Purpose**: Get current user's profile information.

**Endpoint**: `GET /api/v1/users/profile/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "id": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "username": "+989121234567",
  "phone_number": "+989121234567",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "is_active": true,
  "is_driver": true,
  "is_active_driver": true,
  "email_confirmed": true,
  "image_url": "https://example.com/media/profiles/user123.jpg",
  "company_name": "ABC Company",
  "vat_number": "1234567890",
  "bank_name": "Bank of Iran",
  "sheba": "IR123456789012345678901234",
  "birth_date": "1990-01-15",
  "national_id": "1234567890",
  "city": "Tehran",
  "country": "Iran",
  "language": "fa",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Alternative Endpoint**: `GET /api/v1/users/profiles/me/` (same functionality)

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/users/profile/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 2: List User Addresses

**Purpose**: Get all addresses for the current user.

**Endpoint**: `GET /api/v1/users/customer/addresses/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "full_name": "John Doe",
    "address": "No. 10, Example Street, District 1",
    "city": "Tehran",
    "province": "Tehran",
    "latitude": 35.6892,
    "longitude": 51.3890,
    "created_at": "2025-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "full_name": "John Doe",
    "address": "No. 20, Work Street, District 5",
    "city": "Tehran",
    "province": "Tehran",
    "latitude": 35.7000,
    "longitude": 51.4000,
    "created_at": "2025-01-14T09:00:00Z"
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/users/customer/addresses/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 3: Get Address Details

**Purpose**: Get details of a specific address.

**Endpoint**: `GET /api/v1/users/customer/addresses/{id}/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "id": 1,
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone_number": "+989121234567",
  "address": "No. 10, Example Street, District 1",
  "description": "Home address",
  "plate": "12",
  "unit": "3",
  "city": "Tehran",
  "province": "Tehran",
  "country": "Iran",
  "zip_code": "1234567890",
  "latitude": 35.6892,
  "longitude": 51.3890,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/users/customer/addresses/1/" \
  -H "Authorization: Token your-token-here"
```

---

## ✏️ CREATING DATA (Priority 2)

### Step 4: Create Address

**Purpose**: Add a new address to user's address book.

**Endpoint**: `POST /api/v1/users/customer/addresses/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone_number": "+989121234567",
  "address": "No. 10, Example Street, District 1",
  "description": "Home address",
  "plate": "12",
  "unit": "3",
  "city": "Tehran",
  "province": "Tehran",
  "country": "Iran",
  "zip_code": "1234567890",
  "latitude": 35.6892,
  "longitude": 51.3890,
  "company_name": "ABC Company",
  "company_number": "12345",
  "vat_number": "1234567890"
}
```

**Minimal Request**:
```json
{
  "address": "No. 10, Example Street",
  "city": "Tehran"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone_number": "+989121234567",
  "address": "No. 10, Example Street, District 1",
  "description": "Home address",
  "city": "Tehran",
  "province": "Tehran",
  "country": "Iran",
  "zip_code": "1234567890",
  "latitude": 35.6892,
  "longitude": 51.3890,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/customer/addresses/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "No. 10, Example Street",
    "city": "Tehran",
    "latitude": 35.6892,
    "longitude": 51.3890
  }'
```

---

### Step 5: Upload Profile Image

**Purpose**: Upload or update user profile picture.

**Endpoint**: `POST /api/v1/users/upload-image/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: multipart/form-data
```

**Request Body** (Form Data):
```
image: [file - select image file]
```

**Response** (200 OK):
```json
{
  "message": "Profile image uploaded successfully",
  "user": {
    "id": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "phone_number": "+989121234567",
    "first_name": "John",
    "last_name": "Doe",
    "image_url": "https://example.com/media/profiles/user_1234567890.jpg"
  }
}
```

**Response** (400 Bad Request):
```json
{
  "error": "No image file provided"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/upload-image/" \
  -H "Authorization: Token your-token-here" \
  -F "image=@/path/to/image.jpg"
```

---

### Step 6: Add Vehicle (For Drivers)

**Purpose**: Add vehicle information for driver users.

**Endpoint**: `POST /api/v1/users/vehicles/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "model_make": "Toyota",
  "plate_num": "12ABC345",
  "color": "White",
  "year": 2020,
  "vehicle_type": "Van"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "model_make": "Toyota",
  "plate_num": "12ABC345",
  "color": "White",
  "year": 2020,
  "vehicle_type": "Van"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/vehicles/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "model_make": "Toyota",
    "plate_num": "12ABC345",
    "color": "White",
    "year": 2020
  }'
```

---

## ✅ Testing Checklist (In Order)

- [ ] Get user profile
- [ ] List user addresses
- [ ] Get address details
- [ ] Create address
- [ ] Upload profile image
- [ ] Add vehicle (if driver)

---

## 📝 Important Notes

1. **Profile Endpoints**:
   - `GET /api/v1/users/profile/` - Main profile endpoint
   - `GET /api/v1/users/profiles/me/` - Alternative (same functionality)

2. **Address Endpoints**:
   - `GET /api/v1/users/customer/addresses/` - Customer address management
   - `GET /api/v1/users/customer/addresses/{id}/` - Individual address operations

3. **Image Upload**:
   - **Correct endpoint**: `POST /api/v1/users/upload-image/` (not `/profile/upload-image/`)
   - Requires `multipart/form-data` content type
   - Field name: `image`

4. **Vehicle Endpoints**:
   - Only for users with `is_driver=True`
   - `GET /api/v1/users/vehicles/` - List vehicles
   - `POST /api/v1/users/vehicles/` - Add vehicle

---

**Next Step**: [3-products-categories-guide](../3-products-categories-guide/README.md)
