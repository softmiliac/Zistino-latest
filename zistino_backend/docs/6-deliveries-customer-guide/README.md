# 6. Deliveries - Customer Guide

## Overview
This guide covers customer delivery features: viewing pending confirmations, confirming/denying deliveries, submitting surveys, and canceling deliveries.

## 📋 Prerequisites
- Completed [5-orders-guide](../5-orders-guide/README.md)
- Have at least one order with a delivery
- Have a valid authentication token

---

## Step 1: Get Pending Confirmation Deliveries

**Purpose**: Get deliveries waiting for customer confirmation (status: completed, confirmation_status: pending).

**Endpoint**: `GET /api/v1/deliveries/deliveries/pending-confirmation/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK) - With pending deliveries:
```json
{
  "count": 2,
  "deliveries": [
    {
      "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "order_id": "46e818ce-0518-4c64-8438-27bc7163a706",
      "delivered_weight": "30.00",
      "delivery_date": "2025-01-15T10:30:00Z",
      "license_plate_number": "12ABC345",
      "driver_name": "Driver Name",
      "driver_phone": "+989121234567",
      "address": "No. 10, Example Street, Tehran",
      "customer_confirmation_status": "pending",
      "created_at": "2025-01-15T10:00:00Z"
    },
    {
      "id": "xyz98765-4321-0abc-defghijklmnop",
      "order_id": "def45678-9012-3456-7890-abcdefghijkl",
      "delivered_weight": "25.50",
      "delivery_date": "2025-01-14T09:00:00Z",
      "license_plate_number": "12ABC345",
      "driver_name": "Driver Name 2",
      "driver_phone": "+989121234568",
      "address": "No. 20, Another Street, Tehran",
      "customer_confirmation_status": "pending",
      "created_at": "2025-01-14T08:00:00Z"
    }
  ]
}
```

**Response** (200 OK) - No pending deliveries:
```json
{
  "count": 0,
  "deliveries": []
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/deliveries/deliveries/pending-confirmation/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 2: Confirm Delivery

**Purpose**: Confirm a delivery (status must be "completed" and confirmation_status must be "pending"). After confirmation, customer can submit survey.

**Endpoint**: `POST /api/v1/deliveries/deliveries/{delivery_id}/confirm/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{}
```

**Response** (200 OK):
```json
{
  "message": "Delivery confirmed successfully",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "confirmed_at": "2025-01-15T11:00:00Z",
  "customer_confirmation_status": "confirmed"
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "Delivery is not in a state that can be confirmed. Only deliveries with status \"completed\" and confirmation_status \"pending\" can be confirmed."
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/confirm/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Step 3: Deny Delivery

**Purpose**: Deny a delivery with a reason. Delivery must be in "pending" confirmation status.

**Endpoint**: `POST /api/v1/deliveries/deliveries/{delivery_id}/deny/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "denial_reason": "Wrong items delivered. Expected plastic bottles but received paper waste."
}
```

**Response** (200 OK):
```json
{
  "message": "Delivery denied successfully",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "denial_reason": "Wrong items delivered. Expected plastic bottles but received paper waste.",
  "customer_confirmation_status": "denied"
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "Cannot deny when confirmation is not pending."
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/deny/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "denial_reason": "Wrong items delivered."
  }'
```

---

## Step 4: Get Active Survey Questions

**Purpose**: Get active survey questions to display after delivery confirmation.

**Endpoint**: `GET /api/v1/deliveries/deliveries/survey-questions/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "questions": [
    {
      "id": "q1-2345-6789-0abc-defghijklmnop",
      "questionText": "How satisfied were you with the delivery service?",
      "questionType": "rating",
      "options": null,
      "isRequired": true,
      "order": 1
    },
    {
      "id": "q2-3456-7890-1bcd-efghijklmnopq",
      "questionText": "Was the driver on time?",
      "questionType": "yes_no",
      "options": null,
      "isRequired": false,
      "order": 2
    },
    {
      "id": "q3-4567-8901-2cde-fghijklmnopqr",
      "questionText": "What could be improved?",
      "questionType": "text",
      "options": null,
      "isRequired": false,
      "order": 3
    },
    {
      "id": "q4-5678-9012-3def-ghijklmnopqrs",
      "questionText": "Which service did you like most?",
      "questionType": "multiple_choice",
      "options": ["Punctuality", "Professionalism", "Cleanliness", "Communication"],
      "isRequired": false,
      "order": 4
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/deliveries/deliveries/survey-questions/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 5: Submit Delivery Survey

**Purpose**: Submit survey/feedback for a confirmed delivery. Includes overall rating, comment, and answers to custom questions.

**Endpoint**: `POST /api/v1/deliveries/deliveries/{delivery_id}/survey/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body** - With custom question answers:
```json
{
  "rating": 5,
  "comment": "Excellent service! Driver was on time and professional.",
  "answers": [
    {
      "questionId": "q1-2345-6789-0abc-defghijklmnop",
      "answer": "5"
    },
    {
      "questionId": "q2-3456-7890-1bcd-efghijklmnopq",
      "answer": "yes"
    },
    {
      "questionId": "q3-4567-8901-2cde-fghijklmnopqr",
      "answer": "Everything was perfect!"
    },
    {
      "questionId": "q4-5678-9012-3def-ghijklmnopqrs",
      "answer": "Punctuality"
    }
  ]
}
```

**Request Body** - Minimal (only rating):
```json
{
  "rating": 5
}
```

**Response** (201 Created):
```json
{
  "id": "survey123-4567-8901-2abc-defghijklmnop",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "rating": 5,
  "comment": "Excellent service! Driver was on time and professional.",
  "answers": [
    {
      "id": "ans1-2345-6789-0abc-defghijklmnop",
      "questionId": "q1-2345-6789-0abc-defghijklmnop",
      "questionText": "How satisfied were you with the delivery service?",
      "answer": "5"
    },
    {
      "id": "ans2-3456-7890-1bcd-efghijklmnopq",
      "questionId": "q2-3456-7890-1bcd-efghijklmnopq",
      "questionText": "Was the driver on time?",
      "answer": "yes"
    }
  ],
  "created_at": "2025-01-15T11:30:00Z"
}
```

**Response** (400 Bad Request):
```json
{
  "rating": ["Ensure this value is between 1 and 5."]
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/survey/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Excellent service!",
    "answers": [
      {
        "questionId": "q1-2345-6789-0abc-defghijklmnop",
        "answer": "5"
      }
    ]
  }'
```

---

## Step 6: Cancel Delivery

**Purpose**: Cancel a delivery that is awaiting delivery (status: assigned or in_progress). Must provide cancellation reason.

**Endpoint**: `POST /api/v1/deliveries/deliveries/{delivery_id}/cancel/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "cancel_reason": "No longer needed. Will request new delivery later."
}
```

**Response** (200 OK):
```json
{
  "message": "Delivery cancelled successfully",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "cancel_reason": "No longer needed. Will request new delivery later.",
  "status": "cancelled"
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "Cannot cancel delivery. Only deliveries with status 'assigned' or 'in_progress' can be cancelled."
}
```

**Response** (400 Bad Request - Confirmation not pending):
```json
{
  "detail": "Cannot cancel when confirmation is not pending."
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/cancel/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "cancel_reason": "No longer needed."
  }'
```

---

## Step 7: Get Delivery Details

**Purpose**: Get detailed information about a specific delivery.

**Endpoint**: `GET /api/v1/deliveries/deliveries/{delivery_id}/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "order_id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "driver": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "driver_name": "Driver Name",
  "driver_phone": "+989121234567",
  "status": "completed",
  "delivered_weight": "30.00",
  "delivery_date": "2025-01-15T10:30:00Z",
  "license_plate_number": "12ABC345",
  "address": "No. 10, Example Street, Tehran",
  "latitude": "35.6892",
  "longitude": "51.3890",
  "customer_confirmation_status": "confirmed",
  "confirmed_at": "2025-01-15T11:00:00Z",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T11:00:00Z"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/" \
  -H "Authorization: Token your-token-here"
```

---

## ✅ Testing Checklist

- [ ] Get pending confirmation deliveries
- [ ] Confirm a delivery
- [ ] Deny a delivery (with reason)
- [ ] Get active survey questions
- [ ] Submit survey (with rating only)
- [ ] Submit survey (with rating, comment, and answers)
- [ ] Cancel delivery (awaiting delivery)
- [ ] Get delivery details

---

## 💡 Important Notes

1. **Confirmation flow**: 
   - Delivery must be `status="completed"` and `customer_confirmation_status="pending"`
   - After confirmation, customer can submit survey
   - If denied, customer must provide `denial_reason`

2. **Survey questions**: 
   - Get active questions from `/survey-questions/` endpoint
   - Question types: `rating` (1-5), `text`, `yes_no`, `multiple_choice`
   - Required questions must be answered

3. **Cancellation**: 
   - Only deliveries with `status="assigned"` or `status="in_progress"` can be cancelled
   - `customer_confirmation_status` must be "pending"
   - Must provide `cancel_reason`

4. **Weight recording**: 
   - Only confirmed deliveries (`customer_confirmation_status="confirmed"`) are counted in waste weight reports

---

**Next Step**: [7-deliveries-driver-guide](../7-deliveries-driver-guide/README.md)

