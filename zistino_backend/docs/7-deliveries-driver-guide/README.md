# 7. Deliveries - Driver Guide

## Overview
This guide covers driver delivery features: viewing pending deliveries, setting license plate, recording weights per category, center confirmation/denial, and non-delivery recording. **Endpoints are organized by priority: Read first, then Create.**

## 📋 Prerequisites
- Completed [1-authentication-guide](../1-authentication-guide/README.md)
- User must have `is_driver=True`
- Have at least one assigned delivery
- Have a valid authentication token

---

## 📖 READING DATA (Priority 1)

### Step 1: Get Today's Pending Deliveries

**Purpose**: Get all pending deliveries (assigned or in_progress) scheduled for today for the authenticated driver.

**Endpoint**: `GET /api/v1/deliveries/deliveries/today-pending/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK) - With deliveries:
```json
{
  "count": 3,
  "deliveries": [
    {
      "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "driver": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "driver_name": "Driver Name",
      "order": "46e818ce-0518-4c64-8438-27bc7163a706",
      "order_id": "46e818ce-0518-4c64-8438-27bc7163a706",
      "status": "assigned",
      "latitude": "35.6892",
      "longitude": "51.3890",
      "address": "No. 10, Example Street, Tehran",
      "phone_number": "+989121234567",
      "delivery_date": "2025-01-15T10:30:00Z",
      "time_slot_formatted": "8 AM to 12 PM",
      "navigation_url": "https://www.google.com/maps/dir/?api=1&destination=35.6892,51.3890",
      "delivered_weight": "0.00",
      "reminder_sms_sent": false,
      "description": "",
      "created_at": "2025-01-15T08:00:00Z",
      "updated_at": "2025-01-15T08:00:00Z"
    },
    {
      "id": "xyz98765-4321-0abc-defghijklmnop",
      "driver": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "driver_name": "Driver Name",
      "order": "def45678-9012-3456-7890-abcdefghijkl",
      "order_id": "def45678-9012-3456-7890-abcdefghijkl",
      "status": "in_progress",
      "latitude": "35.6893",
      "longitude": "51.3891",
      "address": "No. 20, Another Street, Tehran",
      "phone_number": "+989121234568",
      "delivery_date": "2025-01-15T14:00:00Z",
      "time_slot_formatted": "12 PM to 4 PM",
      "navigation_url": "https://www.google.com/maps/dir/?api=1&destination=35.6893,51.3891",
      "delivered_weight": "0.00",
      "reminder_sms_sent": true,
      "description": "Customer requested morning delivery",
      "created_at": "2025-01-15T07:00:00Z",
      "updated_at": "2025-01-15T08:30:00Z"
    }
  ]
}
```

**Response** (200 OK) - No deliveries:
```json
{
  "count": 0,
  "deliveries": []
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/deliveries/deliveries/today-pending/" \
  -H "Authorization: Token your-token-here"
```

---

### Step 2: Get Delivery Items (Per-Category Weights)

**Purpose**: Get list of delivery items (categories with weights) for a delivery.

**Endpoint**: `GET /api/v1/deliveries/deliveries/{delivery_id}/items/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK) - With items:
```json
{
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "items": [
    {
      "id": "item123-4567-8901-2abc-defghijklmnop",
      "category": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "category_name": "Plastic",
      "weight": "15.00"
    },
    {
      "id": "item234-5678-9012-3bcd-efghijklmnopq",
      "category": "xyz98765-4321-0abc-defghijklmnop",
      "category_name": "Paper",
      "weight": "15.00"
    }
  ],
  "total_weight": "30.00"
}
```

**Response** (200 OK) - No items:
```json
{
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "items": [],
  "total_weight": "0.00"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/items/" \
  -H "Authorization: Token your-token-here"
```

---

## ✏️ CREATING DATA (Priority 2)

### Step 3: Set License Plate Number

**Purpose**: Set license plate number for a delivery (before completing delivery).

**Endpoint**: `POST /api/v1/deliveries/deliveries/{delivery_id}/set-license-plate/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "license_plate_number": "12ABC345"
}
```

**Response** (200 OK):
```json
{
  "message": "License plate number set successfully",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "license_plate_number": "12ABC345"
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Not found."
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/set-license-plate/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "license_plate_number": "12ABC345"
  }'
```

---

### Step 4: Bulk Set Delivery Items (Record Weights Per Category)

**Purpose**: Record weights for each waste category (e.g., Plastic: 15 kg, Paper: 10 kg). This updates `delivered_weight` automatically.

**Endpoint**: `POST /api/v1/deliveries/deliveries/{delivery_id}/items/bulk-set/`

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
    },
    {
      "category": "def45678-9012-3456-7890-abcdefghijkl",
      "weight": "5.00"
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "message": "Delivery items updated successfully",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "items": [
    {
      "id": "item123-4567-8901-2abc-defghijklmnop",
      "category": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "category_name": "Plastic",
      "weight": "15.00"
    },
    {
      "id": "item234-5678-9012-3bcd-efghijklmnopq",
      "category": "xyz98765-4321-0abc-defghijklmnop",
      "category_name": "Paper",
      "weight": "10.00"
    },
    {
      "id": "item345-6789-0123-4cde-fghijklmnopqr",
      "category": "def45678-9012-3456-7890-abcdefghijkl",
      "category_name": "Metal",
      "weight": "5.00"
    }
  ],
  "total_weight": "30.00",
  "delivered_weight": "30.00"
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "Invalid category ID"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/items/bulk-set/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

---

### Step 5: Center Confirm Delivery

**Purpose**: Confirm delivery at the center. This credits customer wallet (based on `waste_price_per_kg` config) and driver wallet (based on `driver_payout_tiers` config). Also handles weight shortfall deduction if applicable.

**Endpoint**: `POST /api/v1/deliveries/deliveries/{delivery_id}/center-confirm/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{}
```

**Response** (200 OK) - With wallet credit:
```json
{
  "message": "Center confirmation recorded. Customer and driver wallets credited.",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "creditedAmount": "300000.00",
  "currency": "Rials",
  "delivery": {
    "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "delivered_weight": "30.00"
  },
  "customer_wallet_balance": "500000.00",
  "driver_wallet_balance": "150000.00",
  "driver_payout_amount": "150000.00",
  "visit_count": 5
}
```

**Response** (200 OK) - With shortfall deduction:
```json
{
  "message": "Center confirmation recorded. Customer and driver wallets credited.",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "creditedAmount": "250000.00",
  "currency": "Rials",
  "delivery": {
    "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "delivered_weight": "30.00"
  },
  "shortfall": {
    "amount": "5.00",
    "minimumWeight": "35.00",
    "estimatedRange": "5-10"
  },
  "shortfallDeduction": "50000.00",
  "baseAmount": "300000.00",
  "customer_wallet_balance": "450000.00",
  "driver_wallet_balance": "150000.00"
}
```

**Response** (200 OK) - No rate configured:
```json
{
  "message": "Center confirmation recorded. No rate configured, wallet not credited.",
  "creditedAmount": "0.00",
  "currency": "Rials",
  "delivery": {
    "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
    "delivered_weight": "30.00"
  }
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "Delivery is not in a state that can be center-confirmed. Only deliveries with status 'completed' can be center-confirmed."
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/center-confirm/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### Step 6: Center Deny Delivery

**Purpose**: Deny delivery at the center with a reason (e.g., insufficient quality, wrong items).

**Endpoint**: `POST /api/v1/deliveries/deliveries/{delivery_id}/center-deny/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "denial_reason": "Insufficient quality. Waste not properly sorted. Contains contaminants."
}
```

**Response** (200 OK):
```json
{
  "message": "Center denial recorded",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "denial_reason": "Insufficient quality. Waste not properly sorted. Contains contaminants.",
  "center_confirmation_status": "denied"
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "Delivery is not in a state that can be center-denied. Only deliveries with status 'completed' can be center-denied."
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/center-deny/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "denial_reason": "Insufficient quality."
  }'
```

---

### Step 7: Record Non-Delivery

**Purpose**: Record that delivery was not completed (e.g., customer not available, address issue) with explanation.

**Endpoint**: `POST /api/v1/deliveries/deliveries/{delivery_id}/non-delivery/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "reason": "Customer not available at address. No response to phone calls."
}
```

**Response** (200 OK):
```json
{
  "message": "Non-delivery recorded successfully",
  "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "reason": "Customer not available at address. No response to phone calls.",
  "status": "non_delivered"
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "Delivery is not in a state that can be marked as non-delivered. Only deliveries with status 'assigned' or 'in_progress' can be marked as non-delivered."
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/deliveries/deliveries/abc12345-def6-7890-ghij-klmnopqrstuv/non-delivery/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Customer not available at address."
  }'
```

---

## ✅ Testing Checklist (In Order)

- [ ] Get today's pending deliveries
- [ ] Get delivery items (empty)
- [ ] Set license plate number
- [ ] Bulk set delivery items (record weights per category)
- [ ] Center confirm delivery (verify wallet credits)
- [ ] Center deny delivery (with reason)
- [ ] Record non-delivery (with reason)

---

## 💡 Important Notes

1. **Delivery workflow**:
   - Driver gets assigned deliveries → Set license plate → Record weights per category → Center confirm/deny

2. **Weight recording**:
   - Use `bulk-set` to record weights per category
   - `delivered_weight` is automatically calculated as sum of item weights

3. **Center confirmation**:
   - Credits customer wallet based on `waste_price_per_kg` config
   - Credits driver wallet based on `driver_payout_tiers` config (tiered by customer visit count)
   - Deducts weight shortfalls if applicable

4. **Configuration required**:
   - `waste_price_per_kg`: Rate per kg for customer credit
   - `driver_payout_tiers`: Tiered payout rates for drivers (based on visit count)

5. **Status flow**:
   - `assigned` → `in_progress` → `completed` → center-confirm/deny

---

**Next Step**: [8-payments-wallet-guide](../8-payments-wallet-guide/README.md)
