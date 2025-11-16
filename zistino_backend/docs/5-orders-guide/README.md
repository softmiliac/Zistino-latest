# 5. Orders Guide

## Overview
This guide covers order creation, viewing orders, waste weight tracking, and waste delivery request configuration.

## 📋 Prerequisites
- Completed [4-basket-guide](../4-basket-guide/README.md)
- Have items in basket
- Have a valid authentication token

---

## Step 1: Get Weight Ranges (For Waste Delivery Request)

**Purpose**: Get available weight ranges for waste delivery request (e.g., "2-5 kg", "5-10 kg").

**Endpoint**: `GET /api/v1/orders/waste/weight-ranges/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "ranges": [
    {
      "value": "2-5",
      "label": "2-5 kg",
      "description": "Light waste (2 to 5 kilograms)"
    },
    {
      "value": "5-10",
      "label": "5-10 kg",
      "description": "Medium waste (5 to 10 kilograms)"
    },
    {
      "value": "10-20",
      "label": "10-20 kg",
      "description": "Heavy waste (10 to 20 kilograms)"
    },
    {
      "value": "20+",
      "label": "20+ kg",
      "description": "Very heavy waste (20+ kilograms)"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/waste/weight-ranges/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 2: Get Time Slots (For Waste Delivery Request)

**Purpose**: Get available time slots for waste pickup (e.g., "8 AM to 12 PM", "12 PM to 4 PM").

**Endpoint**: `GET /api/v1/orders/waste/time-slots/`

**Headers**:
```
Authorization: Token your-token-here
```

**Query Parameters** (Optional):
- `date`: Date in format `YYYY-MM-DD` (default: today)

**Request Body**: None

**Response** (200 OK):
```json
{
  "date": "2025-01-15",
  "slots": [
    {
      "start_time": "08:00:00",
      "end_time": "12:00:00",
      "formatted": "8 AM to 12 PM",
      "is_available": true,
      "available_drivers": 3
    },
    {
      "start_time": "12:00:00",
      "end_time": "16:00:00",
      "formatted": "12 PM to 4 PM",
      "is_available": true,
      "available_drivers": 5
    },
    {
      "start_time": "16:00:00",
      "end_time": "20:00:00",
      "formatted": "4 PM to 8 PM",
      "is_available": false,
      "available_drivers": 0
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/waste/time-slots/?date=2025-01-16" \
  -H "Authorization: Token your-token-here"
```

---

## Step 3: Create Order from Basket

**Purpose**: Convert basket items into an order. Can include location (auto-assigns driver) and waste delivery request details.

**Endpoint**: `POST /api/v1/orders/customer/orders/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body** - Minimal (no location, no driver assignment):
```json
{
  "address1": "No. 10, Example Street, Tehran",
  "phone1": "+989121234567",
  "user_full_name": "John Doe"
}
```

**Request Body** - With location (auto-assigns driver and time slot):
```json
{
  "latitude": 35.6892,
  "longitude": 51.3890,
  "address1": "No. 10, Example Street, Tehran",
  "phone1": "+989121234567",
  "user_full_name": "John Doe"
}
```

**Request Body** - With waste delivery request details:
```json
{
  "latitude": 35.6892,
  "longitude": 51.3890,
  "address1": "No. 10, Example Street, Tehran",
  "phone1": "+989121234567",
  "user_full_name": "John Doe",
  "estimated_weight_range": "5-10",
  "preferred_delivery_date": "2025-01-16T14:00:00Z",
  "payment_method": 1
}
```

**Request Body** - With wallet payment:
```json
{
  "latitude": 35.6892,
  "longitude": 51.3890,
  "address1": "No. 10, Example Street, Tehran",
  "phone1": "+989121234567",
  "user_full_name": "John Doe",
  "payment_method": 1
}
```

**Response** (201 Created) - With wallet payment and location:
```json
{
  "id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "message": "کالاهای سفارش داده شده در تحویل بعدی زباله به شما ارسال خواهد شد",
  "message_en": "Ordered goods will be sent to you in the next waste delivery",
  "payment_method": "wallet",
  "delivery_time_slot": "12 PM to 4 PM",
  "delivery_date": "2025-01-15T12:00:00Z"
}
```

**Response** (201 Created) - With location (driver assigned):
```json
{
  "id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "delivery_time_slot": "12 PM to 4 PM",
  "delivery_date": "2025-01-15T12:00:00Z"
}
```

**Response** (201 Created) - Basic order:
```json
{
  "id": "46e818ce-0518-4c64-8438-27bc7163a706"
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "basket is empty"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/orders/customer/orders/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 35.6892,
    "longitude": 51.3890,
    "address1": "No. 10, Example Street, Tehran",
    "phone1": "+989121234567",
    "user_full_name": "John Doe",
    "estimated_weight_range": "5-10",
    "preferred_delivery_date": "2025-01-16T14:00:00Z"
  }'
```

---

## Step 4: List Customer Orders

**Purpose**: Get list of customer's orders (last 20 orders).

**Endpoint**: `GET /api/v1/orders/customer/orders/`

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
      "id": "46e818ce-0518-4c64-8438-27bc7163a706",
      "status": "pending",
      "total_price": "125.50",
      "created_at": "2025-01-15T10:30:00Z"
    },
    {
      "id": "xyz98765-4321-0abc-defghijklmnop",
      "status": "confirmed",
      "total_price": "250.00",
      "created_at": "2025-01-14T09:00:00Z"
    }
  ],
  "total": 5
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/customer/orders/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 5: Search Customer Orders

**Purpose**: Search customer orders with pagination and keyword filter.

**Endpoint**: `POST /api/v1/orders/customer/orders/client/search/`

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
  "keyword": ""
}
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "46e818ce-0518-4c64-8438-27bc7163a706",
      "status": "pending",
      "total_price": "125.50",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pageNumber": 1,
  "pageSize": 20,
  "total": 5
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/orders/customer/orders/client/search/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "pageNumber": 1,
    "pageSize": 20,
    "keyword": ""
  }'
```

---

## Step 6: Get Order Details

**Purpose**: Get detailed information about a specific order.

**Endpoint**: `GET /api/v1/orders/customer/orders/{order_id}/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "status": "pending",
  "total_price": "125.50",
  "created_at": "2025-01-15T10:30:00Z",
  "address1": "No. 10, Example Street, Tehran",
  "phone1": "+989121234567",
  "user_full_name": "John Doe",
  "estimated_weight_range": "5-10",
  "preferred_delivery_date": "2025-01-16T14:00:00Z"
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Not found"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/customer/orders/46e818ce-0518-4c64-8438-27bc7163a706/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 7: Get Waste Weight Summary

**Purpose**: Get summary of waste weights delivered (only confirmed deliveries).

**Endpoint**: `GET /api/v1/orders/waste/weight-summary/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "total_weight": "125.50",
  "total_deliveries": 5,
  "average_weight_per_delivery": "25.10",
  "last_delivery_date": "2025-01-15T10:30:00Z",
  "last_delivery_weight": "30.00"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/waste/weight-summary/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 8: Get Waste Weight History

**Purpose**: Get history of waste weight deliveries with pagination.

**Endpoint**: `GET /api/v1/orders/waste/weight-history/`

**Headers**:
```
Authorization: Token your-token-here
```

**Query Parameters** (Optional):
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

**Request Body**: None

**Response** (200 OK):
```json
{
  "items": [
    {
      "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "order_id": "46e818ce-0518-4c64-8438-27bc7163a706",
      "weight": "30.00",
      "delivery_date": "2025-01-15T10:30:00Z",
      "driver_name": "Driver Name",
      "status": "confirmed"
    },
    {
      "delivery_id": "xyz98765-4321-0abc-defghijklmnop",
      "order_id": "def45678-9012-3456-7890-abcdefghijkl",
      "weight": "25.50",
      "delivery_date": "2025-01-14T09:00:00Z",
      "driver_name": "Driver Name 2",
      "status": "confirmed"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/waste/weight-history/?page=1&page_size=20" \
  -H "Authorization: Token your-token-here"
```

---

## Step 9: Get Order Weight Details

**Purpose**: Get detailed weight information for a specific order.

**Endpoint**: `GET /api/v1/orders/waste/orders/{order_id}/weights/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "order_id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "estimated_weight_range": "5-10",
  "deliveries": [
    {
      "delivery_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "delivered_weight": "30.00",
      "delivery_date": "2025-01-15T10:30:00Z",
      "driver_name": "Driver Name",
      "categories": [
        {
          "category_name": "Plastic",
          "weight": "15.00"
        },
        {
          "category_name": "Paper",
          "weight": "15.00"
        }
      ]
    }
  ],
  "total_weight": "30.00"
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Order not found"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/waste/orders/46e818ce-0518-4c64-8438-27bc7163a706/weights/" \
  -H "Authorization: Token your-token-here"
```

---

## ✅ Testing Checklist

- [ ] Get weight ranges
- [ ] Get time slots
- [ ] Create order from basket (minimal)
- [ ] Create order with location
- [ ] Create order with waste delivery request details
- [ ] Create order with wallet payment
- [ ] List customer orders
- [ ] Search customer orders
- [ ] Get order details
- [ ] Get waste weight summary
- [ ] Get waste weight history
- [ ] Get order weight details

---

## 💡 Important Notes

1. **Basket must have items**: Order creation requires items in basket
2. **Location triggers auto-assignment**: Providing `latitude` and `longitude` automatically assigns a driver from matching zone
3. **Time slot selection**: If location provided, system selects nearest available time slot
4. **Weight ranges**: Get from `/weight-ranges/` endpoint
5. **Time slots**: Get from `/time-slots/` endpoint
6. **Payment method**: `1` = wallet credit, `0` or `null` = other methods
7. **Weight tracking**: Only confirmed deliveries (`customer_confirmation_status='confirmed'`) are counted in weight reports

---

**Next Step**: [6-deliveries-customer-guide](../6-deliveries-customer-guide/README.md)

