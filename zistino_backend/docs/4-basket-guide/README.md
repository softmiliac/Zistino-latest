# 4. Basket Management Guide

## Overview
This guide covers shopping basket operations: viewing basket, adding items, and applying coupons. **Endpoints are organized by priority: Read first, then Create.**

## 📋 Prerequisites
- Completed [3-products-categories-guide](../3-products-categories-guide/README.md)
- Have a valid authentication token
- Know product IDs from previous steps

---

## 📖 READING DATA (Priority 1)

### Step 1: Get Basket

**Purpose**: Get current user's shopping basket with all items.

**Endpoint**: `GET /api/v1/baskets/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK) - Basket with items:
```json
{
  "id": 1,
  "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "total_items": 5,
  "total_unique_items": 3,
  "cart_total": 150000,
  "is_empty": false,
  "items": [
    {
      "id": 1,
      "product": "46e818ce-0518-4c64-8438-27bc7163a706",
      "name": "Plastic Bottles",
      "quantity": 2,
      "price": 50000,
      "item_total": 100000,
      "discount_percent": 10,
      "master_image": "https://example.com/media/products/bottles.jpg"
    },
    {
      "id": 2,
      "product": "xyz98765-4321-0abc-defghijklmnop",
      "name": "Paper Waste",
      "quantity": 3,
      "price": 30000,
      "item_total": 90000,
      "discount_percent": 0
    }
  ]
}
```

**Response** (200 OK) - Empty basket:
```json
{
  "id": 1,
  "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "total_items": 0,
  "total_unique_items": 0,
  "cart_total": 0,
  "is_empty": true,
  "items": []
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/baskets/" \
  -H "Authorization: Token your-token-here"
```

---

## ✏️ CREATING DATA (Priority 2)

### Step 2: Add Item to Basket

**Purpose**: Add a product to the shopping basket. If product already exists, quantity will be increased.

**Endpoint**: `POST /api/v1/baskets/items/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "product": "46e818ce-0518-4c64-8438-27bc7163a706",
  "quantity": 2,
  "price": 50000,
  "name": "Plastic Bottles",
  "description": "Clean plastic bottles for recycling",
  "master_image": "https://example.com/media/products/bottles.jpg",
  "discount_percent": 10
}
```

**Alternative Field Names** (also accepted):
```json
{
  "product_id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "quantity": 1,
  "unit_price": 50000,
  "name": "Plastic Bottles"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "total_items": 2,
  "total_unique_items": 1,
  "cart_total": 100000,
  "is_empty": false,
  "items": [
    {
      "id": 1,
      "product": "46e818ce-0518-4c64-8438-27bc7163a706",
      "name": "Plastic Bottles",
      "quantity": 2,
      "price": 50000,
      "item_total": 100000,
      "discount_percent": 10
    }
  ]
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "product_id and price are required"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/baskets/items/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "46e818ce-0518-4c64-8438-27bc7163a706",
    "quantity": 2,
    "price": 50000,
    "name": "Plastic Bottles"
  }'
```

---

### Step 3: Apply Coupon

**Purpose**: Apply a discount coupon to the basket.

**Endpoint**: `POST /api/v1/baskets/apply-coupon/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body** - Apply coupon:
```json
{
  "code": "SUMMER25"
}
```

**Request Body** - Remove coupon:
```json
{
  "code": ""
}
```

**Response** (200 OK) - Coupon applied:
```json
{
  "id": 1,
  "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "total_items": 5,
  "total_unique_items": 3,
  "cart_total": 125000,
  "is_empty": false,
  "applied_coupon": {
    "key": "SUMMER25",
    "amount": 25000
  },
  "items": [
    {
      "id": 1,
      "product": "46e818ce-0518-4c64-8438-27bc7163a706",
      "quantity": 2,
      "price": 50000,
      "item_total": 100000
    }
  ]
}
```

**Response** (400 Bad Request) - Invalid coupon:
```json
{
  "detail": "invalid coupon"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/baskets/apply-coupon/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{"code": "SUMMER25"}'
```

---

## ✅ Testing Checklist (In Order)

- [ ] Get empty basket
- [ ] Add first item to basket
- [ ] Add second item to basket
- [ ] Apply coupon
- [ ] Verify basket totals

---

## 💡 Tips

1. **Basket is auto-created**: First call to get basket creates it automatically
2. **Quantity increments**: Adding same product again increases quantity
3. **Coupon validation**: Coupon must be active and valid
4. **Cart total**: Includes discounts from coupons

---

**Next Step**: [5-orders-guide](../5-orders-guide/README.md)
