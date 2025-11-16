# 9. Points & Lottery Guide

## Overview
This guide covers points balance, transaction history, referral system, and lottery participation.

## 📋 Prerequisites
- Completed [1-authentication-guide](../1-authentication-guide/README.md)
- Have a valid authentication token

---

## Step 1: Get Points Balance

**Purpose**: Get current points balance for the logged-in customer.

**Endpoint**: `GET /api/v1/points/my-balance/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "balance": 150,
  "lifetimeEarned": 200,
  "lifetimeSpent": 50
}
```

**Response** (200 OK) - New user:
```json
{
  "balance": 0,
  "lifetimeEarned": 0,
  "lifetimeSpent": 0
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/points/my-balance/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 2: Get Points Transaction History

**Purpose**: Get points transaction history (last 100 transactions) for the logged-in customer.

**Endpoint**: `GET /api/v1/points/my-history/`

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
      "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "userPhone": "+989121234567",
      "amount": 10,
      "transactionType": "earned",
      "source": "order",
      "referenceId": "46e818ce-0518-4c64-8438-27bc7163a706",
      "description": "Points for order 46e818ce-0518-4c64-8438-27bc7163a706",
      "balanceAfter": 10,
      "createdAt": "2025-01-15T10:30:00Z"
    },
    {
      "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "userPhone": "+989121234567",
      "amount": 5,
      "transactionType": "earned",
      "source": "referral",
      "referenceId": "xyz98765-4321-0abc-defghijklmnop",
      "description": "Referral points for referring +989121234568",
      "balanceAfter": 15,
      "createdAt": "2025-01-14T09:00:00Z"
    },
    {
      "id": "def45678-9012-3456-7890-abcdefghijkl",
      "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "userPhone": "+989121234567",
      "amount": -100,
      "transactionType": "spent",
      "source": "lottery",
      "referenceId": "lottery-123",
      "description": "Points spent on lottery tickets",
      "balanceAfter": 5,
      "createdAt": "2025-01-13T08:00:00Z"
    }
  ],
  "total": 15
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/points/my-history/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 3: Get My Referral Code

**Purpose**: Get or create referral code for the logged-in user.

**Endpoint**: `GET /api/v1/referrals/my-code/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "referralCode": "ABC12345",
  "referralUrl": "https://app.example.com/register?ref=ABC12345"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/referrals/my-code/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 4: Get My Referrals

**Purpose**: Get list of people I referred. Shows referral status and whether points were awarded.

**Endpoint**: `GET /api/v1/referrals/my-referrals/`

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
      "referrerId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "referrerPhone": "+989121234567",
      "referrerName": "John Doe",
      "referredId": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "referredPhone": "+989121234568",
      "referredName": "Jane Smith",
      "referral_code": "ABC12345",
      "status": "completed",
      "referrerPointsAwarded": true,
      "referredBonusAwarded": false,
      "completedAt": "2025-01-15T10:30:00Z",
      "createdAt": "2025-01-14T09:00:00Z"
    },
    {
      "id": "xyz98765-4321-0abc-defghijklmnop",
      "referrerId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "referrerPhone": "+989121234567",
      "referrerName": "John Doe",
      "referredId": "def45678-9012-3456-7890-abcdefghijkl",
      "referredPhone": "+989121234569",
      "referredName": "Bob Wilson",
      "referral_code": "ABC12345",
      "status": "pending",
      "referrerPointsAwarded": false,
      "referredBonusAwarded": false,
      "completedAt": null,
      "createdAt": "2025-01-16T08:00:00Z"
    }
  ],
  "total": 3
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/referrals/my-referrals/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 5: Get Active Lotteries

**Purpose**: Get list of active lotteries that customers can participate in.

**Endpoint**: `GET /api/v1/lotteries/active/`

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
      "title": "Monthly Prize Draw",
      "description": "Win an amazing Electric Scooter! Participate now!",
      "prizeName": "Electric Scooter",
      "prizeImage": "https://example.com/images/scooter.jpg",
      "ticketPricePoints": 100,
      "status": "active",
      "startDate": "2025-01-01T00:00:00Z",
      "endDate": "2025-12-31T23:59:59Z",
      "totalTickets": 150,
      "totalParticipants": 50,
      "winnerId": null,
      "winnerName": null,
      "createdAt": "2025-01-01T00:00:00Z"
    },
    {
      "id": "xyz98765-4321-0abc-defghijklmnop",
      "title": "Holiday Special",
      "description": "Special holiday lottery!",
      "prizeName": "Smartphone",
      "prizeImage": "https://example.com/images/phone.jpg",
      "ticketPricePoints": 200,
      "status": "active",
      "startDate": "2025-12-01T00:00:00Z",
      "endDate": "2025-12-31T23:59:59Z",
      "totalTickets": 75,
      "totalParticipants": 30,
      "winnerId": null,
      "winnerName": null,
      "createdAt": "2025-11-15T10:00:00Z"
    }
  ],
  "total": 2
}
```

**Response** (200 OK) - No active lotteries:
```json
{
  "items": [],
  "total": 0
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/lotteries/active/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 5.5: Get Lottery Details

**Purpose**: Get detailed information about a specific lottery.

**Endpoint**: `GET /api/v1/lotteries/{lottery_id}/detail/`

**Headers**:
```
Authorization: Token your-token-here
```

**Request Body**: None

**Response** (200 OK):
```json
{
  "id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "title": "Monthly Prize Draw",
  "description": "Win an amazing Electric Scooter! Participate now!",
  "prizeName": "Electric Scooter",
  "prizeImage": "https://example.com/images/scooter.jpg",
  "ticketPricePoints": 100,
  "status": "active",
  "startDate": "2025-01-01T00:00:00Z",
  "endDate": "2025-12-31T23:59:59Z",
  "totalTickets": 150,
  "totalParticipants": 50,
  "winnerId": null,
  "winnerName": null,
  "createdAt": "2025-01-01T00:00:00Z"
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Lottery not found"
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/lotteries/46e818ce-0518-4c64-8438-27bc7163a706/detail/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 6: Buy Lottery Tickets

**Purpose**: Buy lottery tickets using points. Points will be deducted from balance.

**Endpoint**: `POST /api/v1/lotteries/{lottery_id}/buy-tickets/`

**Headers**:
```
Authorization: Token your-token-here
Content-Type: application/json
```

**Request Body** - Buy 5 tickets:
```json
{
  "ticket_count": 5
}
```

**Request Body** - Buy 1 ticket:
```json
{
  "ticket_count": 1
}
```

**Response** (200 OK):
```json
{
  "ticket_id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "ticket_count": 5,
  "points_spent": 500,
  "remaining_balance": 450
}
```

**Response** (400 Bad Request) - Insufficient points:
```json
{
  "detail": "Insufficient points. Need 500, have 300"
}
```

**Response** (400 Bad Request) - Lottery not active:
```json
{
  "detail": "Lottery is not active",
  "reasons": [
    "Status is 'draft' (must be 'active')",
    "Start date is in the future: 2025-12-31T00:00:00Z"
  ],
  "current_status": "draft",
  "start_date": "2025-12-31T00:00:00Z",
  "end_date": "2026-12-31T23:59:59Z",
  "current_time": "2025-01-15T10:30:00Z"
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Lottery not found"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/lotteries/46e818ce-0518-4c64-8438-27bc7163a706/buy-tickets/" \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_count": 5
  }'
```

---

## Step 7: Get My Lottery Tickets

**Purpose**: Get all lottery tickets purchased by logged-in customer across all lotteries.

**Endpoint**: `GET /api/v1/lotteries/my-tickets/`

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
      "lotteryId": "xyz98765-4321-0abc-defghijklmnop",
      "lotteryTitle": "Monthly Prize Draw",
      "lotteryPrizeName": "Electric Scooter",
      "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "userPhone": "+989121234567",
      "ticketCount": 5,
      "pointsSpent": 500,
      "purchaseDate": "2025-01-15T10:30:00Z",
      "isWinner": false
    },
    {
      "id": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "lotteryId": "xyz98765-4321-0abc-defghijklmnop",
      "lotteryTitle": "Monthly Prize Draw",
      "lotteryPrizeName": "Electric Scooter",
      "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "userPhone": "+989121234567",
      "ticketCount": 3,
      "pointsSpent": 300,
      "purchaseDate": "2025-01-14T09:00:00Z",
      "isWinner": false
    },
    {
      "id": "def45678-9012-3456-7890-abcdefghijkl",
      "lotteryId": "46e818ce-0518-4c64-8438-27bc7163a706",
      "lotteryTitle": "Holiday Special",
      "lotteryPrizeName": "Smartphone",
      "userId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "userPhone": "+989121234567",
      "ticketCount": 1,
      "pointsSpent": 200,
      "purchaseDate": "2025-01-13T08:00:00Z",
      "isWinner": true
    }
  ],
  "total": 10
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/lotteries/my-tickets/" \
  -H "Authorization: Token your-token-here"
```

---

## Step 8: Get Past Lottery Winners

**Purpose**: Get list of past lottery winners.

**Endpoint**: `GET /api/v1/lotteries/winners/`

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
      "title": "Monthly Prize Draw - January",
      "description": "January monthly lottery",
      "prizeName": "Electric Scooter",
      "prizeImage": "https://example.com/images/scooter.jpg",
      "ticketPricePoints": 100,
      "status": "drawn",
      "startDate": "2025-01-01T00:00:00Z",
      "endDate": "2025-01-31T23:59:59Z",
      "winnerId": "0641067f-df76-416c-98cd-6f89e43d3b3f",
      "winnerName": "John Doe",
      "winnerTicketId": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "drawnAt": "2025-02-01T10:30:00Z",
      "totalTickets": 200,
      "totalParticipants": 75,
      "createdAt": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 5
}
```

**cURL Example**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/lotteries/winners/" \
  -H "Authorization: Token your-token-here"
```

---

## ✅ Testing Checklist

- [ ] Get points balance
- [ ] Get points transaction history
- [ ] Get my referral code
- [ ] Get my referrals
- [ ] Get active lotteries
- [ ] Buy lottery tickets
- [ ] Get my lottery tickets
- [ ] Get past lottery winners

---

## 💡 Important Notes

1. **Points earning**:
   - Points earned from orders (automatic)
   - Points earned from referrals (when referred user completes registration/order)

2. **Points spending**:
   - Buying lottery tickets
   - Other features (if implemented)

3. **Referral system**:
   - Each user has a unique referral code
   - Referrer gets points when referred user completes actions
   - Referred user may get bonus points

4. **Lottery**:
   - Only active lotteries are shown
   - Tickets cost points (configured per lottery)
   - Winner is selected when lottery is drawn (admin action)

---

**Next Step**: [10-manager-guide](../10-manager-guide/README.md)

