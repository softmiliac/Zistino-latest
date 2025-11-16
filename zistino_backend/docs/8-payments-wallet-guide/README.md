# 8. Payments & Wallet Guide

## Overview
This guide covers wallet balance, transaction history, deposit requests, and credit/receipt reports.

## 📋 Prerequisites
- Completed [1-authentication-guide](../1-authentication-guide/README.md)
- Have a valid authentication token

---

## Step 1: Get Wallet Balance

**Purpose**: Get current wallet balance for the logged-in user.

**Endpoint**: `GET /api/v1/payments/transactionwallet/mytransactionwallettotal`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "total": "500000.00"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/payments/transactionwallet/mytransactionwallettotal" \
  -H "Authorization: Token your-token-here"
```

---

## Step 2: Get Transaction History

**Purpose**: Get transaction history (last 100 transactions) for the logged-in user.

**Endpoint**: `GET /api/v1/payments/transactionwallet/mytransactionwallethistory`

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
    "wallet": "xyz98765-4321-0abc-defghijklmnop",
    "amount": "100000.00",
    "transaction_type": "credit",
    "description": "Credit from waste delivery",
    "reference_id": "delivery-123",
    "created_at": "2025-01-15T10:30:00Z"
  },
  {
    "id": "def45678-9012-3456-7890-abcdefghijkl",
    "wallet": "xyz98765-4321-0abc-defghijklmnop",
    "amount": "-50000.00",
    "transaction_type": "debit",
    "description": "Order payment",
    "reference_id": "order-456",
    "created_at": "2025-01-14T09:00:00Z"
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/payments/transactionwallet/mytransactionwallethistory" \
  -H "Authorization: Token your-token-here"
```

---

## Step 3: Get Credits and Receipts Report

**Purpose**: Get summary report of total credits made and total receipts submitted.

**Endpoint**: `GET /api/v1/payments/transactionwallet/my-report`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK) - With credits and receipts:
```json
{
  "totalCredits": "250000.00",
  "creditCount": 5,
  "totalReceipts": "150000.00",
  "receiptCount": 3,
  "currency": "Rials"
}
```

**Response** (200 OK) - New customer:
```json
{
  "totalCredits": "0.00",
  "creditCount": 0,
  "totalReceipts": "0.00",
  "receiptCount": 0,
  "currency": "Rials"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/payments/transactionwallet/my-report" \
  -H "Authorization: Token your-token-here"
```

---

## Step 4: Create Deposit Request

**Purpose**: Create a deposit request to add money to wallet. SMS confirmation will be sent automatically.

**Endpoint**: `POST /api/v1/payments/deposits/request/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body** - Basic deposit request:
```json
{
  "amount": 100000
}
```

**Request Body** - With bank reference number:
```json
{
  "amount": 50000,
  "reference_id": "BANK-RECEIPT-12345"
}
```

**Response** (201 Created):
```json
{
  "id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "amount": "100000.00",
  "status": "pending",
  "reference_id": "",
  "createdAt": "2025-01-15T10:30:00Z"
}
```

**Response** (400 Bad Request):
```json
{
  "amount": ["This field is required."]
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments/deposits/request/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100000
  }'
```

---

## Step 5: List My Deposit Requests

**Purpose**: Get list of all deposit requests for the logged-in user.

**Endpoint**: `GET /api/v1/payments/deposits/my-requests/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
[
  {
    "id": "46e818ce-0518-4c64-8438-27bc7163a706",
    "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "userPhone": "+989121234567",
    "amount": "100000.00",
    "status": "approved",
    "reference_id": "BANK-RECEIPT-12345",
    "approvedAt": "2025-01-15T11:00:00Z",
    "createdAt": "2025-01-15T10:30:00Z"
  },
  {
    "id": "xyz98765-4321-0abc-defghijklmnop",
    "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "userPhone": "+989121234567",
    "amount": "50000.00",
    "status": "pending",
    "reference_id": "",
    "approvedAt": null,
    "createdAt": "2025-01-14T09:00:00Z"
  },
  {
    "id": "def45678-9012-3456-7890-abcdefghijkl",
    "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "userPhone": "+989121234567",
    "amount": "75000.00",
    "status": "rejected",
    "reference_id": "BANK-RECEIPT-67890",
    "rejectionReason": "Invalid reference number",
    "approvedAt": null,
    "createdAt": "2025-01-13T08:00:00Z"
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/payments/deposits/my-requests/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 6: Get Deposit Request Details

**Purpose**: Get detailed information about a specific deposit request.

**Endpoint**: `GET /api/v1/payments/deposits/my-requests/{request_id}/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "user": "0641067f-df76-416c-98cd-6f89e43d3b3f",
  "userPhone": "+989121234567",
  "amount": "100000.00",
  "status": "approved",
  "reference_id": "BANK-RECEIPT-12345",
  "approvedAt": "2025-01-15T11:00:00Z",
  "createdAt": "2025-01-15T10:30:00Z",
  "updatedAt": "2025-01-15T11:00:00Z"
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
curl -X GET "http://127.0.0.1:8000/api/v1/payments/deposits/my-requests/46e818ce-0518-4c64-8438-27bc7163a706/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 7: Apply Coupon to Basket

**Purpose**: Apply a discount coupon to the current basket.

**Endpoint**: `POST /api/v1/payments/coupons/applycoupononbasket`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "code": "SUMMER25"
}
```

**Response** (200 OK):
```json
{
  "message": "Coupon applied successfully",
  "coupon": {
    "key": "SUMMER25",
    "amount": 25000
  },
  "basket": {
    "id": 1,
    "total_items": 5,
    "cart_total": 125000,
    "original_total": 150000
  }
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "invalid coupon"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments/coupons/applycoupononbasket" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SUMMER25"
  }'
```

---

## ✅ Testing Checklist

- [ ] Get wallet balance
- [ ] Get transaction history
- [ ] Get credits and receipts report
- [ ] Create deposit request (basic)
- [ ] Create deposit request (with reference)
- [ ] List deposit requests
- [ ] Get deposit request details
- [ ] Apply coupon to basket

---

## 💡 Important Notes

1. **Wallet balance**: Auto-created when first accessed
2. **Deposit requests**: 
   - Status: `pending` → `approved` or `rejected`
   - When approved, wallet is credited automatically
   - SMS confirmation sent on create/approve/reject
3. **Credits**: Wallet credit transactions (from waste deliveries, manual credits, etc.)
4. **Receipts**: Deposit requests with `reference_id` (bank receipt reference numbers)
5. **Transaction types**: 
   - `credit`: Money added to wallet
   - `debit`: Money deducted from wallet

---

**Next Step**: [9-points-lottery-guide](../9-points-lottery-guide/README.md)

