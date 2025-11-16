# 3. Products & Categories Guide

## Overview
This guide covers browsing products, categories, and store items. **Endpoints are organized by priority: Read first, then Create.**

## 📋 Prerequisites
- Completed [2-user-profile-guide](../2-user-profile-guide/README.md)
- Have a valid authentication token

---

## 📖 READING DATA (Priority 1)

### Step 1: List Categories

**Purpose**: Get all product categories.

**Endpoint**: `GET /api/v1/products/categories/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
[
  {
    "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "name": "Plastic",
    "description": "Plastic waste category",
    "image_url": "https://example.com/media/categories/plastic.jpg",
    "is_active": true
  },
  {
    "id": "xyz98765-4321-0abc-defghijklmnop",
    "name": "Paper",
    "description": "Paper waste category",
    "image_url": "https://example.com/media/categories/paper.jpg",
    "is_active": true
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/products/categories/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 2: Get Category Details

**Purpose**: Get details of a specific category.

**Endpoint**: `GET /api/v1/products/categories/{id}/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "name": "Plastic",
  "description": "Plastic waste category including bottles, containers, etc.",
  "image_url": "https://example.com/media/categories/plastic.jpg",
  "is_active": true,
  "products": [
    {
      "id": "46e818ce-0518-4c64-8438-27bc7163a706",
      "name": "Plastic Bottles",
      "price": 50000
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/products/categories/abc12345-def6-7890-ghij-klmnopqrstuv/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 3: List Products

**Purpose**: Get all products (with optional filtering).

**Endpoint**: `GET /api/v1/products/products/`

**Headers**:
```
Authorization: Token your-token-here
```

**Query Parameters** (Optional):
- `category`: Filter by category ID
- `search`: Search in product name/description

**Request Body**: None

**Response** (200 OK):
```json
[
  {
    "id": "46e818ce-0518-4c64-8438-27bc7163a706",
    "name": "Plastic Bottles",
    "description": "Clean plastic bottles for recycling",
    "category": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "category_name": "Plastic",
    "price": 50000,
    "image_url": "https://example.com/media/products/bottles.jpg",
    "is_active": true,
    "stock_quantity": 100
  },
  {
    "id": "xyz98765-4321-0abc-defghijklmnop",
    "name": "Paper Waste",
    "description": "Clean paper waste",
    "category": "xyz98765-4321-0abc-defghijklmnop",
    "category_name": "Paper",
    "price": 30000,
    "image_url": "https://example.com/media/products/paper.jpg",
    "is_active": true,
    "stock_quantity": 50
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/products/products/?category=abc12345-def6-7890-ghij-klmnopqrstuv" \
  -H "Authorization: Token your-token-here"
```

---

### Step 4: Get Product Details

**Purpose**: Get detailed information about a specific product.

**Endpoint**: `GET /api/v1/products/products/{id}/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "name": "Plastic Bottles",
  "description": "Clean plastic bottles for recycling. Must be empty and clean.",
  "category": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "category_name": "Plastic",
  "price": 50000,
  "image_url": "https://example.com/media/products/bottles.jpg",
  "is_active": true,
  "stock_quantity": 100,
  "specifications": [
    {
      "id": 1,
      "name": "Weight",
      "value": "500g per unit"
    },
    {
      "id": 2,
      "name": "Condition",
      "value": "Must be clean and empty"
    }
  ],
  "colors": [
    {
      "id": 1,
      "name": "Clear",
      "hex": "#FFFFFF"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/products/products/46e818ce-0518-4c64-8438-27bc7163a706/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 5: Get Product Comments

**Purpose**: Get comments/reviews for a product.

**Endpoint**: `GET /api/v1/products/products/{id}/comments/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "product_id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "comments": [
    {
      "id": 1,
      "user_full_name": "John Doe",
      "user_image_url": "https://example.com/media/profiles/user.jpg",
      "rate": 5,
      "text": "Great product! Very satisfied.",
      "is_accepted": true,
      "created_on": "2025-01-15T10:00:00Z",
      "children": []
    }
  ],
  "total": 1,
  "average_rating": 5.0
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/products/products/46e818ce-0518-4c64-8438-27bc7163a706/comments/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 6: Get Product Codes (For Products with Codes)

**Purpose**: Get product codes (e.g., SIM card recharge codes) for a product.

**Endpoint**: `GET /api/v1/products/products/{product_id}/codes/`

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
    "product": "46e818ce-0518-4c64-8438-27bc7163a706",
    "productName": "SIM Card Recharge 10000",
    "code": "1234567890123456",
    "status": "unused",
    "assigned_to": null,
    "assigned_at": null,
    "used_at": null,
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/products/products/46e818ce-0518-4c64-8438-27bc7163a706/codes/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 7: Search Products

**Purpose**: Search products by keyword.

**Endpoint**: `GET /api/v1/products/products/?search=keyword`

**Headers**:
```
Authorization: Token your-token-here
```

**Query Parameters**:
- `search`: Search keyword

**Request Body**: None

**Response** (200 OK):
```json
[
  {
    "id": "46e818ce-0518-4c64-8438-27bc7163a706",
    "name": "Plastic Bottles",
    "description": "Clean plastic bottles",
    "price": 50000,
    "category_name": "Plastic"
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/products/products/?search=plastic" \
  -H "Authorization: Token your-token-here"
```

---

## ✏️ CREATING DATA (Priority 2)

### Step 8: Add Product Comment

**Purpose**: Add a comment/review to a product.

**Endpoint**: `POST /api/v1/products/comments/commentsbyproductidasync`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "productId": "46e818ce-0518-4c64-8438-27bc7163a706",
  "rate": 5,
  "text": "Excellent product quality! Very satisfied with the service.",
  "parent": null
}
```

**Response** (201 Created):
```json
{
  "id": 2,
  "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "product": "46e818ce-0518-4c64-8438-27bc7163a706",
  "rate": 5,
  "text": "Excellent product quality! Very satisfied with the service.",
  "is_accepted": false,
  "user_full_name": "John Doe",
  "created_on": "2025-01-15T11:00:00Z"
}
```

**Response** (400 Bad Request):
```json
{
  "rate": ["Ensure this value is between 1 and 5."]
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/products/comments/commentsbyproductidasync" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "46e818ce-0518-4c64-8438-27bc7163a706",
    "rate": 5,
    "text": "Excellent product quality!"
  }'
```

---

## ✅ Testing Checklist (In Order)

- [ ] List all categories
- [ ] Get category details
- [ ] List all products
- [ ] Get product details
- [ ] Get product comments
- [ ] Get product codes (if applicable)
- [ ] Search products
- [ ] Add product comment

---

**Next Step**: [4-basket-guide](../4-basket-guide/README.md)
