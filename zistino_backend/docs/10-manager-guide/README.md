# 10. Manager/Admin Guide

## Overview
This guide covers all manager/admin endpoints for managing deliveries, users, payments, reports, configurations, and system settings.

## 📋 Prerequisites
- Completed [1-authentication-guide](../1-authentication-guide/README.md)
- User must have `is_staff=True` (manager/admin)
- Have a valid authentication token

---

## 🔐 Important Notes

**Manager endpoints require:**
- Valid authentication token
- User must have `is_staff=True` (`is_staff` field in User model)
- All endpoints are under `/api/v1/manager/` or `/api/v1/payments/manager/` or `/api/v1/products/manager/`

**To create a manager user:**
1. Create superuser: `python manage.py createsuperuser`
2. Or set `is_staff=True` in Django Admin for existing user

---

## 📦 Deliveries Management

### Step 1: List All Deliveries

**Endpoint**: `GET /api/v1/manager/deliveries/`

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
    "driver": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "driver_name": "Driver Name",
    "order": "46e818ce-0518-4c64-8438-27bc7163a706",
    "status": "completed",
    "delivered_weight": "30.00",
    "delivery_date": "2025-01-15T10:30:00Z",
    "address": "No. 10, Example Street, Tehran"
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/manager/deliveries/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 2: Create Delivery (Manual)

**Endpoint**: `POST /api/v1/manager/deliveries/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "order": "46e818ce-0518-4c64-8438-27bc7163a706",
  "driver": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "status": "assigned",
  "delivery_date": "2025-01-16T10:00:00Z",
  "description": "Manual delivery assignment"
}
```

**Response** (201 Created):
```json
{
  "id": "xyz98765-4321-0abc-defghijklmnop",
  "order": "46e818ce-0518-4c64-8438-27bc7163a706",
  "driver": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "status": "assigned",
  "delivery_date": "2025-01-16T10:00:00Z"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/manager/deliveries/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "order": "46e818ce-0518-4c64-8438-27bc7163a706",
    "driver": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "status": "assigned"
  }'
```

---

### Step 3: Calculate Delivery Price

**Endpoint**: `GET /api/v1/manager/deliveries/{delivery_id}/price/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "deliveryId": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "currency": "Rials",
  "breakdown": [
    {
      "category": "Plastic",
      "categoryId": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "weight": "15.00",
      "rate": "10000.00",
      "amount": "150000.00"
    },
    {
      "category": "Paper",
      "categoryId": "xyz98765-4321-0abc-defghijklmnop",
      "weight": "10.00",
      "rate": "8000.00",
      "amount": "80000.00"
    }
  ],
  "totalWeight": "25.00",
  "totalAmount": "230000.00",
  "rateSource": "category_rates_per_kg"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/manager/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/price/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 4: Set Delivery Items (Manager Override)

**Endpoint**: `POST /api/v1/manager/deliveries/{delivery_id}/items/bulk-set/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "items": [
    {
      "category": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "weight": "15.00"
    },
    {
      "category": "xyz98765-4321-0abc-defghijklmnop",
      "weight": "10.00"
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "message": "Delivery items updated successfully",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "total_weight": "25.00"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/manager/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/items/bulk-set/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "category": "abc12345-def6-7890-ghij-klmnopqrstuv",
        "weight": "15.00"
      }
    ]
  }'
```

---

### Step 5: Transfer Delivery to Another Driver

**Endpoint**: `POST /api/v1/manager/deliveries/{delivery_id}/transfer/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "new_driver_id": "xyz98765-4321-0abc-defghijklmnop",
  "reason": "Original driver unavailable"
}
```

**Response** (200 OK):
```json
{
  "message": "Delivery transferred successfully",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "old_driver": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "new_driver": "xyz98765-4321-0abc-defghijklmnop"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/manager/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/transfer/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "new_driver_id": "xyz98765-4321-0abc-defghijklmnop",
    "reason": "Original driver unavailable"
  }'
```

---

## 📞 Telephone Requests

### Step 6: Create Telephone Request

**Endpoint**: `POST /api/v1/manager/telephone-requests/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body** - Minimal:
```json
{
  "phoneNumber": "+989121234567",
  "fullName": "John Doe",
  "address": "No. 10, Example Street, Tehran"
}
```

**Request Body** - With items and delivery:
```json
{
  "phoneNumber": "+989121234567",
  "fullName": "John Doe",
  "address": "No. 10, Example Street, Tehran",
  "latitude": 35.6892,
  "longitude": 51.3890,
  "preferredDeliveryDate": "2025-01-16T14:00:00Z",
  "createDelivery": true,
  "items": [
    {
      "productName": "Plastic",
      "weight": "8.50",
      "quantity": 1
    },
    {
      "productName": "Paper",
      "weight": "4.00",
      "quantity": 1
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "message": "Telephone request created",
  "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "orderId": "46e818ce-0518-4c64-8438-27bc7163a706",
  "deliveryId": "abc12345-def6-7890-ghij-klmnopqrstuv"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/manager/telephone-requests/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+989121234567",
    "fullName": "John Doe",
    "address": "No. 10, Example Street, Tehran"
  }'
```

---

## 👥 User Management

### Step 7: Get Users by Role

**Endpoint**: `POST /api/v1/users/users/userbyrole`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body** - Get all drivers:
```json
{
  "role": "driver",
  "isActive": true
}
```

**Request Body** - Get all active users:
```json
{
  "isActive": true
}
```

**Response** (200 OK):
```json
[
  {
    "id": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "phone_number": "+989121234567",
    "first_name": "John",
    "last_name": "Doe",
    "is_driver": true,
    "is_active": true
  }
]
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/users/userbyrole" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "driver",
    "isActive": true
  }'
```

---

## 💰 Payment Management

### Step 8: Record Manual Payment

**Endpoint**: `POST /api/v1/payments/manager/payments/record/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body** - Credit customer:
```json
{
  "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "amount": 100000,
  "transactionType": "credit",
  "description": "Manual credit from admin panel"
}
```

**Request Body** - Debit customer:
```json
{
  "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "amount": 50000,
  "transactionType": "debit",
  "description": "Manual debit for refund"
}
```

**Response** (200 OK):
```json
{
  "message": "Payment recorded successfully",
  "transactionId": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "amount": "100000.00",
  "transactionType": "credit",
  "newBalance": "600000.00"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments/manager/payments/record/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "amount": 100000,
    "transactionType": "credit",
    "description": "Manual credit"
  }'
```

---

### Step 9: Get Customer Credits Report

**Endpoint**: `POST /api/v1/payments/manager/customer-credits/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "pageNumber": 1,
  "pageSize": 20,
  "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "startDate": "2025-01-01T00:00:00Z",
  "endDate": "2025-01-31T23:59:59Z"
}
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "userPhone": "+989121234567",
      "totalCredits": "250000.00",
      "creditCount": 5,
      "lastCreditDate": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 10,
  "pageNumber": 1,
  "pageSize": 20
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments/manager/customer-credits/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "pageNumber": 1,
    "pageSize": 20
  }'
```

---

### Step 10: Get Driver Credits Report

**Endpoint**: `POST /api/v1/payments/manager/driver-credits/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "pageNumber": 1,
  "pageSize": 20,
  "driverId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "startDate": "2025-01-01T00:00:00Z",
  "endDate": "2025-01-31T23:59:59Z"
}
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "driverId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "driverPhone": "+989121234567",
      "driverName": "Driver Name",
      "totalPayout": "500000.00",
      "payoutCount": 10,
      "visitCount": 25,
      "averagePayoutPerVisit": "20000.00",
      "lastPayoutDate": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 5,
  "pageNumber": 1,
  "pageSize": 20
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments/manager/driver-credits/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "pageNumber": 1,
    "pageSize": 20
  }'
```

---

## ❌ Disapprovals Management

### Step 11: View Disapprovals

**Endpoint**: `POST /api/v1/manager/disapprovals/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "pageNumber": 1,
  "pageSize": 20,
  "type": "customer_denial",
  "startDate": "2025-01-01T00:00:00Z",
  "endDate": "2025-01-31T23:59:59Z"
}
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "type": "customer_denial",
      "deliveryId": "xyz98765-4321-0abc-defghijklmnop",
      "customerId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "customerPhone": "+989121234567",
      "reason": "Wrong items delivered",
      "createdAt": "2025-01-15T10:30:00Z"
    },
    {
      "id": "def45678-9012-3456-7890-abcdefghijkl",
      "type": "driver_non_delivery",
      "deliveryId": "ghi78901-2345-6789-0abc-defghijklmn",
      "driverId": "jkl01234-5678-9012-3bcd-efghijklmnop",
      "driverPhone": "+989121234568",
      "reason": "Customer not available",
      "createdAt": "2025-01-14T09:00:00Z"
    }
  ],
  "total": 15,
  "pageNumber": 1,
  "pageSize": 20
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/manager/disapprovals/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "pageNumber": 1,
    "pageSize": 20
  }'
```

---

## 🚗 Driver Tracking

### Step 12: Get Driver Routes

**Endpoint**: `POST /api/v1/manager/drivers/{driver_id}/routes/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "date": "2025-01-15"
}
```

**Response** (200 OK):
```json
{
  "driverId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "driverPhone": "+989121234567",
  "date": "2025-01-15",
  "trips": [
    {
      "tripId": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "startTime": "2025-01-15T08:00:00Z",
      "endTime": "2025-01-15T16:00:00Z",
      "distance": 45.5,
      "duration": 28800,
      "pickups": [
        {
          "deliveryId": "xyz98765-4321-0abc-defghijklmnop",
          "address": "No. 10, Example Street",
          "latitude": 35.6892,
          "longitude": 51.3890,
          "arrivalTime": "2025-01-15T09:00:00Z",
          "departureTime": "2025-01-15T09:15:00Z",
          "dwellTime": 900
        }
      ]
    }
  ],
  "summary": {
    "totalTrips": 1,
    "totalDistance": 45.5,
    "totalDuration": 28800,
    "totalPickups": 3,
    "averageTimePerPickup": 900
  }
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/manager/drivers/0641067f-df76-416c-98cd-6f89e43d3b3f/routes/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-01-15"
  }'
```

---

### Step 13: Get Driver Available Dates

**Endpoint**: `GET /api/v1/manager/drivers/{driver_id}/available-dates/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "driverId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "dates": [
    "2025-01-15",
    "2025-01-14",
    "2025-01-13"
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/manager/drivers/0641067f-df76-416c-98cd-6f89e43d3b3f/available-dates/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 14: Get Driver Satisfaction

**Endpoint**: `POST /api/v1/manager/drivers/satisfaction/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "pageNumber": 1,
  "pageSize": 20,
  "driverId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "startDate": "2025-01-01T00:00:00Z",
  "endDate": "2025-01-31T23:59:59Z"
}
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "driverId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "driverPhone": "+989121234567",
      "driverName": "Driver Name",
      "averageRating": 4.5,
      "totalRatings": 20,
      "ratingDistribution": {
        "5": 10,
        "4": 7,
        "3": 2,
        "2": 1,
        "1": 0
      },
      "surveys": [
        {
          "deliveryId": "abc12345-def6-7890-ghij-klmnopqrstuv",
          "rating": 5,
          "comment": "Excellent service",
          "createdAt": "2025-01-15T10:30:00Z"
        }
      ]
    }
  ],
  "total": 5,
  "pageNumber": 1,
  "pageSize": 20
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/manager/drivers/satisfaction/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "pageNumber": 1,
    "pageSize": 20
  }'
```

---

## ⚖️ Weight Configuration

### Step 15: Configure Weight Range Minimums

**Endpoint**: `POST /api/v1/manager/weight-range-minimums/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "ranges": [
    {
      "value": "2-5",
      "min": 2.0
    },
    {
      "value": "5-10",
      "min": 5.0
    },
    {
      "value": "10-20",
      "min": 10.0
    },
    {
      "value": "20+",
      "min": 20.0
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "message": "Weight range minimums configured successfully",
  "ranges": [
    {
      "value": "2-5",
      "min": 2.0
    },
    {
      "value": "5-10",
      "min": 5.0
    }
  ]
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/manager/weight-range-minimums/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "ranges": [
      {
        "value": "2-5",
        "min": 2.0
      },
      {
        "value": "5-10",
        "min": 5.0
      }
    ]
  }'
```

---

### Step 16: View Weight Shortfalls

**Endpoint**: `POST /api/v1/manager/weight-shortfalls/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "pageNumber": 1,
  "pageSize": 20,
  "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "isDeducted": false,
  "startDate": "2025-01-01T00:00:00Z",
  "endDate": "2025-01-31T23:59:59Z"
}
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "userPhone": "+989121234567",
      "deliveryId": "xyz98765-4321-0abc-defghijklmnop",
      "estimated_range": "5-10",
      "minimum_weight": "5.00",
      "delivered_weight": "3.50",
      "shortfallAmount": "-1.50",
      "is_deducted": false,
      "createdAt": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 5,
  "pageNumber": 1,
  "pageSize": 20
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/manager/weight-shortfalls/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "pageNumber": 1,
    "pageSize": 20
  }'
```

---

## 📋 Survey Management

### Step 17: List Survey Questions

**Endpoint**: `GET /api/v1/manager/survey-questions/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "q1-2345-6789-0abc-defghijklmnop",
      "questionText": "How satisfied were you with the delivery service?",
      "questionType": "rating",
      "options": null,
      "isActive": true,
      "isRequired": true,
      "order": 1,
      "createdAt": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 5
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/manager/survey-questions/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 18: Create Survey Question

**Endpoint**: `POST /api/v1/manager/survey-questions/create/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body** - Rating question:
```json
{
  "questionText": "How satisfied were you with the delivery service?",
  "questionType": "rating",
  "isActive": true,
  "isRequired": true,
  "order": 1
}
```

**Request Body** - Multiple choice question:
```json
{
  "questionText": "Which service did you like most?",
  "questionType": "multiple_choice",
  "options": ["Punctuality", "Professionalism", "Cleanliness", "Communication"],
  "isActive": true,
  "isRequired": false,
  "order": 2
}
```

**Response** (201 Created):
```json
{
  "id": "q1-2345-6789-0abc-defghijklmnop",
  "questionText": "How satisfied were you with the delivery service?",
  "questionType": "rating",
  "isActive": true,
  "isRequired": true,
  "order": 1
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/manager/survey-questions/create/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "questionText": "How satisfied were you?",
    "questionType": "rating",
    "isRequired": true,
    "order": 1
  }'
```

---

### Step 19: Update Survey Question

**Endpoint**: `PUT /api/v1/manager/survey-questions/{question_id}/update/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "questionText": "Updated question text",
  "questionType": "rating",
  "isActive": true,
  "isRequired": false,
  "order": 2
}
```

**Response** (200 OK):
```json
{
  "id": "q1-2345-6789-0abc-defghijklmnop",
  "questionText": "Updated question text",
  "questionType": "rating",
  "isActive": true,
  "isRequired": false,
  "order": 2
}
```

**cURL Example**:
```bash
curl -X PUT "http://127.0.0.1:8000/api/v1/manager/survey-questions/q1-2345-6789-0abc-defghijklmnop/update/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "questionText": "Updated question",
    "isActive": true
  }'
```

---

### Step 20: Delete Survey Question

**Endpoint**: `DELETE /api/v1/manager/survey-questions/{question_id}/delete/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "message": "Survey question deleted successfully"
}
```

**cURL Example**:
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/manager/survey-questions/q1-2345-6789-0abc-defghijklmnop/delete/" \
  -H "Authorization: Token your-token-here"
```

---

## 🎁 Product Codes Management

### Step 21: List Product Codes

**Endpoint**: `GET /api/v1/products/products/{product_id}/codes/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "productId": "46e818ce-0518-4c64-8438-27bc7163a706",
  "productName": "SIM Card Recharge 10000",
  "items": [
    {
      "id": "code123-4567-890a-bcde-fghijklmnop",
      "code": "1234567890123456",
      "status": "unused",
      "assignedAt": null
    }
  ],
  "total": 10,
  "pageNumber": 1,
  "pageSize": 20
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/products/products/46e818ce-0518-4c64-8438-27bc7163a706/codes/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 22: Bulk Import Product Codes

**Endpoint**: `POST /api/v1/products/products/{product_id}/codes/bulk-import/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "codes": [
    "1234567890123456",
    "2345678901234567",
    "3456789012345678"
  ]
}
```

**Response** (200 OK):
```json
{
  "imported": 3,
  "skipped": 0,
  "message": "Product codes imported successfully"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/products/products/46e818ce-0518-4c64-8438-27bc7163a706/codes/bulk-import/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "codes": [
      "1234567890123456",
      "2345678901234567"
    ]
  }'
```

---

## ⚙️ System Configuration

### Step 23: Delivery Reminder Check

**Purpose**: Manually trigger the task that checks for deliveries needing reminder SMS and sends them. The automatic task runs every 15 minutes via Celery Beat.

**Endpoint**: `POST /api/v1/deliveries/reminder-check/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None (no request body required)

**What it does:**
- Finds deliveries scheduled between 45-75 minutes from now
- Sends reminder SMS to customers
- Marks deliveries as having reminder sent (`reminder_sms_sent=True`)

**Response** (200 OK) - Success:
```json
{
  "message": "Delivery reminder check completed successfully",
  "checked": 5,
  "sent": 3,
  "failed": 0,
  "timestamp": "2025-01-15T10:30:00.123456Z"
}
```

**Response** (200 OK) - No deliveries found:
```json
{
  "message": "Delivery reminder check completed successfully",
  "checked": 0,
  "sent": 0,
  "failed": 0,
  "timestamp": "2025-01-15T10:30:00.123456Z"
}
```

**Response** (500 Internal Server Error) - Error:
```json
{
  "message": "Delivery reminder check failed",
  "error": "Error message here",
  "timestamp": "2025-01-15T10:30:00.123456Z"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/deliveries/reminder-check/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json"
```

**Note**: This endpoint requires manager permissions (`is_staff=True`). The automatic task runs via Celery Beat every 15 minutes, but this endpoint allows manual triggering for testing or immediate execution.

---

## ✅ Testing Checklist

- [ ] List all deliveries
- [ ] Create delivery manually
- [ ] Calculate delivery price
- [ ] Set delivery items (manager override)
- [ ] Transfer delivery
- [ ] Create telephone request
- [ ] Get users by role
- [ ] Record manual payment
- [ ] Get customer credits report
- [ ] Get driver credits report
- [ ] View disapprovals
- [ ] Get driver routes
- [ ] Get driver available dates
- [ ] Get driver satisfaction
- [ ] Configure weight range minimums
- [ ] View weight shortfalls
- [ ] List survey questions
- [ ] Create survey question
- [ ] Update survey question
- [ ] Delete survey question
- [ ] List product codes
- [ ] Bulk import product codes
- [ ] Trigger delivery reminder check

---

## 💡 Important Notes

1. **Manager permissions**: All endpoints require `is_staff=True`
2. **Configuration**: 
   - Weight range minimums: Configure via `/weight-range-minimums/`
   - Category rates: Configure via Django Admin `Configuration` model (`category_rates_per_kg`)
   - Waste price: Configure via Django Admin `Configuration` model (`waste_price_per_kg`)
   - Driver payout tiers: Configure via Django Admin `Configuration` model (`driver_payout_tiers`)

3. **Reports**: 
   - Customer credits: Sum of all credit transactions
   - Driver credits: Sum of all driver payout transactions (tiered by visit count)
   - Weight shortfalls: Created when delivered weight < minimum weight

4. **Survey questions**:
   - Types: `rating`, `text`, `yes_no`, `multiple_choice`
   - Active questions are shown to customers after delivery confirmation

---

**End of Documentation** 🎉

You've completed all guides! Your backend API is fully documented and ready for frontend integration.

