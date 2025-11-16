# New Developer Guide - Complete System Walkthrough

## Overview

This guide explains how to use the Zistino backend API system step by step. It covers everything from authentication to creating orders, explaining what is required and why each component exists.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Step 1: Authentication - Verification Code and Registration](#step-1-authentication)
3. [Step 2: Login](#step-2-login)
4. [Step 3: Understanding Required Entities](#step-3-understanding-required-entities)
5. [Step 4: Categories - Why We Need Them](#step-4-categories)
6. [Step 5: Products - Core of the System](#step-5-products)
7. [Step 6: Basket - Shopping Cart Before Order](#step-6-basket)
8. [Step 7: Orders - Converting Basket to Purchase](#step-7-orders)
9. [Step 8: Configurations - Essential System Settings](#step-8-configurations)
10. [Step 9: Addresses](#step-9-addresses)
11. [Step 10: Zones](#step-10-zones)
12. [Step 11: UserPoints](#step-11-userpoints)
13. [Step 12: Wallet](#step-12-wallet)
14. [Step 13: Transactions](#step-13-transactions)
15. [Step 14: Deposits](#step-14-deposits)
16. [Step 15: SMS](#step-15-sms)
17. [Complete Workflow Summary](#complete-workflow-summary)
18. [Additional API Endpoints Reference](#additional-api-endpoints-reference)
19. [Complete System Overview](#complete-system-overview)

---

## Getting Started

Before you begin, make sure:
- Django server is running (`python manage.py runserver`)
- You have access to Django Admin Panel at `http://127.0.0.1:8000/admin/`
- You have API testing tool (Postman, Insomnia, or cURL)
- You understand basic REST API concepts

---

## Step 1: Authentication

### Why Verification Code is Required

The system uses **phone number verification** for security. Users cannot register or login without verifying their phone number first. This prevents fake accounts and ensures each user has a valid phone number.

### Process Flow

1. **Request Verification Code** - User sends their phone number
2. **Receive Code** - System sends 6-digit code via SMS (or returns in response for testing)
3. **Verify Code** - User must provide the correct code
4. **Register or Login** - Use the verified code to create account or access existing account

### Required Steps

#### Step 1.1: Send Verification Code

**Endpoint**: `POST /api/v1/auth/send-code/`

**What happens:**
- System generates a 6-digit random code
- Code is saved in database with expiration time (5 minutes)
- Code is sent to user's phone via SMS
- In development, code may be returned in response

**Required Field:**
- `phone_number` (string) - Format: `+989121234567` (with country code)

**Why this is first:** Without verification, users cannot proceed. This is the foundation of user authentication.

---

#### Step 1.2: Register New User

**Endpoint**: `POST /api/v1/auth/register/`

**When to use:** When creating a new user account for the first time.

**Required Fields:**
- `phone_number` (string) - Must match the phone number used in send-code
- `code` (string) - The 6-digit verification code received

**Optional Fields:**
- `first_name` (string)
- `last_name` (string)
- `email` (string)

**What happens:**
- System verifies the code is valid and not expired
- Creates new user account in database
- Generates authentication token
- Returns token and user information

**Why registration is needed:** Users must exist in the system before they can:
- Browse products
- Add items to basket
- Create orders
- Access any protected features

**Important:** Save the `token` from response - you need it for all authenticated API calls!

---

## Step 2: Login

### Why Login is Needed

After registration, users need to login to:
- Access their account
- Get a new authentication token
- Access protected endpoints

### Process

**Endpoint**: `POST /api/v1/auth/login/`

**Required Fields:**
- `phone_number` (string) - Existing user's phone number
- `code` (string) - Verification code from send-code

**What happens:**
- System verifies the code
- Finds existing user by phone number
- Generates/retrieves authentication token
- Returns token and user information

**Note:** If user doesn't exist, use register endpoint instead.

---

## Step 3: Understanding Required Entities

### Entity Dependency Chain

The system has a specific order in which entities must be created:

```
User (from authentication)
    ↓
Category (required for products)
    ↓
Product (required for basket and orders)
    ↓
Basket (required for orders)
    ↓
Order (final purchase)
```

### Why This Order Matters

- **User** must exist first - everything belongs to a user
- **Category** must exist before **Product** - products need categories
- **Product** must exist before **Basket** - you can't add products that don't exist
- **Basket** must have items before **Order** - orders are created from basket
- **Order** requires all previous entities

---

## Step 4: Categories

### Why Categories Are Required

Categories organize products into groups. Every product must belong to a category. This is essential for:
- Organizing products (e.g., "Plastic Waste", "Paper Waste", "Metal Waste")
- Filtering products by type
- Better user experience (users can browse by category)
- System structure and organization

### Essential Fields

**Required:**
- `name` (string) - Category name (e.g., "Plastic Waste")

**Optional but Recommended:**
- `description` (string) - What this category contains
- `image` (file) - Category image for display
- `is_active` (boolean) - Whether category is visible (default: true)

### How to Create

**Via Django Admin:**
1. Go to `Products` → `Categories` → `Add Category`
2. Enter category name
3. Add description and image (optional)
4. Save

**Via API:**
- `GET /api/v1/products/categories/` - List all categories
- `GET /api/v1/products/categories/{id}/` - Get category details

**Note:** Categories are typically created by administrators, not regular users.

---

## Step 5: Products

### Why Products Are Required

Products are the core of the system. Without products:
- Users cannot add anything to basket
- Orders cannot be created
- The entire commerce system doesn't work

### Essential Fields

**Required:**
- `name` (string) - Product name (e.g., "Plastic Bottles")
- `category` (foreign key) - Must link to existing Category
- `price_per_unit` (decimal) - Price for one unit
- `unit` (string) - Unit of measurement (e.g., "kg", "piece", "ton")

**Optional but Important:**
- `description` (string) - Product details
- `image` (file) - Product image
- `is_active` (boolean) - Whether product is available (default: true)
- `stock_quantity` (integer) - How many items in stock

### How to Create

**Via Django Admin:**
1. Go to `Products` → `Products` → `Add Product`
2. Enter product name
3. Select category (use search icon to find category)
4. Enter price and unit
5. Add description and image (optional)
6. Save

**Via API:**
- `GET /api/v1/products/products/` - List all products
- `GET /api/v1/products/products/{id}/` - Get product details
- `GET /api/v1/products/products/?category={category_id}` - Filter by category

**Why category is required:** Products must be organized. You cannot create a product without selecting a category first.

---

## Step 6: Basket

### Why Basket is Required

Basket (shopping cart) is the intermediate step between browsing products and creating orders. It allows users to:
- Add multiple products before purchasing
- Review items before checkout
- Modify quantities
- Apply coupons/discounts
- Calculate total price

### Why Not Create Orders Directly?

Baskets provide:
- **Flexibility** - Users can add/remove items before finalizing
- **Price calculation** - System calculates totals, discounts, coupons
- **User experience** - Standard e-commerce flow (browse → add to cart → checkout)
- **Data integrity** - Separates "wishlist" from "purchase"

### Essential Fields

**Basket is auto-created** when user first accesses it. No manual creation needed.

**Basket Items Required Fields:**
- `product` (string/UUID) - Product ID to add
- `quantity` (integer) - How many units
- `price` (integer) - Price per unit (must match product price)

**Optional:**
- `name` (string) - Product name (for display)
- `discount_percent` (integer) - Discount percentage

### How to Use

**Get Basket:**
- `GET /api/v1/baskets/` - Get current user's basket (creates empty basket if doesn't exist)

**Add Item to Basket:**
- `POST /api/v1/baskets/items/` - Add product to basket

**Apply Coupon:**
- `POST /api/v1/baskets/apply-coupon/` - Apply discount coupon

### Why Basket Must Have Items Before Order

- Orders are created **from basket items**
- Empty basket = no items to order
- System converts basket items to order items automatically
- This ensures data consistency

---

## Step 7: Orders

### Why Orders Are Required

Orders represent the final purchase. They:
- Convert basket items into a permanent purchase record
- Track order status (pending, confirmed, completed, etc.)
- Enable delivery management
- Record payment information
- Generate invoices and receipts

### Essential Fields

**Required:**
- Basket must have items (orders are created from basket)
- `total_price` (integer) - Total order amount (calculated from basket)

**Optional but Recommended:**
- `address1` (string) - Delivery address
- `phone1` (string) - Contact phone number
- `user_full_name` (string) - Customer name
- `latitude` (decimal) - Customer location (for driver assignment)
- `longitude` (decimal) - Customer location (for driver assignment)
- `estimated_weight_range` (string) - For waste delivery (e.g., "5-10")
- `preferred_delivery_date` (datetime) - When customer wants delivery
- `payment_method` (integer) - 1 = wallet, 0 = other

### How to Create

**Endpoint**: `POST /api/v1/orders/customer/orders/`

**What happens:**
- System gets user's current basket
- Checks basket has items (returns error if empty)
- Creates order with basket total price
- Converts basket items to order items
- Clears basket (or keeps it, depending on system settings)
- If location provided, automatically assigns driver from matching zone
- If location provided, automatically selects nearest available time slot
- Returns order ID and confirmation

### Why Order Needs Basket

- Orders are created **from basket contents**
- Empty basket = no items to order = error
- This ensures users only order items they selected
- Maintains data integrity

### Order Status Values

- `0` = Pending (just created)
- `1` = Confirmed (approved)
- `2` = In Progress (being processed)
- `3` = Completed (finished)
- `4` = Cancelled

### Related Endpoints

- `GET /api/v1/orders/customer/orders/` - List user's orders
- `GET /api/v1/orders/customer/orders/{id}/` - Get order details
- `POST /api/v1/orders/customer/orders/client/search/` - Search orders
- `GET /api/v1/orders/waste/weight-ranges/` - Get weight ranges for waste delivery
- `GET /api/v1/orders/waste/time-slots/` - Get available time slots for delivery

---

## Step 8: Configurations

### Why Configurations Are Required

Configurations store system-wide settings that can be changed without modifying code. These are essential for:
- Points system settings (how many points per order, per referral)
- Weight range configurations
- Time slot settings
- Payment settings
- Feature flags

### Essential Configurations

**Points System (Required if using points/lottery):**
- `order_points` - Points awarded per completed order (default: 1)
- `referral_points` - Points awarded per successful referral (default: 2)

**Weight Ranges (Required for waste delivery):**
- Weight range configurations (e.g., "2-5", "5-10", "10-20", "20+")

**Time Slots (Required for delivery scheduling):**
- Delivery time slot configurations (e.g., "8 AM to 12 PM", "12 PM to 4 PM")

### How to Configure

**Via Django Admin:**
1. Go to `Configurations` → `Configurations` → `Add Configuration`
2. Enter configuration name (e.g., "order_points")
3. Set value (e.g., `{"amount": 1}`)
4. Set type (number, string, etc.)
5. Set `is_active` to true
6. Save

**Via API:**
- Configurations are typically managed by administrators
- Regular users can view active configurations but not modify them

### Why Configurations Matter

- **Flexibility** - Managers can change settings without code deployment
- **Business Rules** - Points, discounts, delivery rules can be adjusted
- **Testing** - Easy to test different configurations
- **Maintenance** - Settings stored in database, not hard-coded

---

## Complete Workflow Summary

### For New Users (First Time)

1. **Authentication**
   - `POST /api/v1/auth/send-code/` - Request verification code
   - `POST /api/v1/auth/register/` - Register with code
   - Save authentication token

2. **Browse Products**
   - `GET /api/v1/products/categories/` - See available categories
   - `GET /api/v1/products/products/` - See available products
   - `GET /api/v1/products/products/{id}/` - View product details

3. **Add to Basket**
   - `GET /api/v1/baskets/` - Get/create basket
   - `POST /api/v1/baskets/items/` - Add products to basket
   - `POST /api/v1/baskets/apply-coupon/` - Apply discount (optional)

4. **Create Order**
   - `GET /api/v1/orders/waste/weight-ranges/` - Get weight ranges (if waste delivery)
   - `GET /api/v1/orders/waste/time-slots/` - Get time slots (if waste delivery)
   - `POST /api/v1/orders/customer/orders/` - Create order from basket

5. **View Orders**
   - `GET /api/v1/orders/customer/orders/` - List your orders
   - `GET /api/v1/orders/customer/orders/{id}/` - View order details

### For Returning Users

1. **Login**
   - `POST /api/v1/auth/send-code/` - Request verification code
   - `POST /api/v1/auth/login/` - Login with code
   - Save authentication token

2. Continue from "Browse Products" above

### For Administrators (Django Admin)

1. **Setup Categories**
   - Create categories first (required for products)

2. **Setup Products**
   - Create products linked to categories

3. **Setup Configurations**
   - Configure points system
   - Configure weight ranges
   - Configure time slots

4. **Manage Orders**
   - View all orders
   - Update order status
   - Assign drivers

---

## Essential Field Checklist

### User Registration
- ✅ `phone_number` (required)
- ✅ `code` (required - from verification)

### Category
- ✅ `name` (required)

### Product
- ✅ `name` (required)
- ✅ `category` (required - must exist)
- ✅ `price_per_unit` (required)
- ✅ `unit` (required)

### Basket Item
- ✅ `product` (required - product ID)
- ✅ `quantity` (required)
- ✅ `price` (required)

### Order
- ✅ Basket must have items (required)
- ✅ `total_price` (calculated from basket)
- Optional: `address1`, `phone1`, `latitude`, `longitude`

### Configuration
- ✅ `name` (required)
- ✅ `value` (required)
- ✅ `type` (required)
- ✅ `is_active` (required - set to true)

---

## Why Each Component Exists

| Component | Purpose | Why Required |
|-----------|---------|--------------|
| **User** | User accounts | All actions belong to a user |
| **Category** | Product organization | Products must be categorized |
| **Product** | Items to sell/buy | Core of commerce system |
| **Basket** | Shopping cart | Allows users to select multiple items before purchase |
| **Order** | Final purchase | Permanent record of transaction |
| **Configuration** | System settings | Flexible business rules without code changes |

---

## Common Mistakes to Avoid

1. **Trying to create product without category** - Category must exist first
2. **Trying to create order with empty basket** - Add items to basket first
3. **Forgetting to save authentication token** - Token needed for all authenticated requests
4. **Using expired verification code** - Codes expire in 5 minutes
5. **Creating order without products** - Products must exist before basket/orders
6. **Missing required fields** - Check API documentation for required fields

---

## Next Steps

After understanding this guide:

1. **Test Authentication Flow**
   - Send verification code
   - Register new user
   - Login with existing user

2. **Test Product Flow**
   - View categories (via admin or API)
   - View products
   - Understand product structure

3. **Test Basket Flow**
   - Get basket (creates empty basket)
   - Add items to basket
   - View basket with items

4. **Test Order Flow**
   - Create order from basket
   - View order details
   - Understand order status

5. **Explore Additional Features**
   - Wallet/payments
   - Deliveries
   - Points and lottery
   - User profiles and addresses

---

## API Endpoints Reference

### Authentication
- `POST /api/v1/auth/send-code/` - Request verification code
- `POST /api/v1/auth/verify-code/` - Verify code (validation only)
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login existing user
- `POST /api/v1/auth/logout/` - Logout user

### Products & Categories
- `GET /api/v1/products/categories/` - List categories
- `GET /api/v1/products/categories/{id}/` - Get category details
- `GET /api/v1/products/products/` - List products
- `GET /api/v1/products/products/{id}/` - Get product details
- `GET /api/v1/products/products/?category={id}` - Filter products by category
- `GET /api/v1/products/products/?search={keyword}` - Search products

### Basket
- `GET /api/v1/baskets/` - Get basket
- `POST /api/v1/baskets/items/` - Add item to basket
- `PUT /api/v1/baskets/{id}/items/` - Update basket item
- `DELETE /api/v1/baskets/{id}/items/` - Remove basket item
- `POST /api/v1/baskets/apply-coupon/` - Apply coupon

### Orders
- `GET /api/v1/orders/customer/orders/` - List customer orders
- `POST /api/v1/orders/customer/orders/` - Create order from basket
- `GET /api/v1/orders/customer/orders/{id}/` - Get order details
- `POST /api/v1/orders/customer/orders/client/search/` - Search orders
- `GET /api/v1/orders/waste/weight-ranges/` - Get weight ranges
- `GET /api/v1/orders/waste/time-slots/` - Get time slots
- `GET /api/v1/orders/waste/weight-summary/` - Get weight summary
- `GET /api/v1/orders/waste/weight-history/` - Get weight history

### User Profile
- `GET /api/v1/users/profile/` - Get user profile
- `PUT /api/v1/users/profile/` - Update user profile
- `POST /api/v1/users/upload-image/` - Upload profile image
- `GET /api/v1/users/customer/addresses/` - List addresses
- `POST /api/v1/users/customer/addresses/` - Create address

---

## Summary

**Required Order:**
1. User (via authentication)
2. Category (before products)
3. Product (before basket)
4. Basket (before orders)
5. Order (final purchase)

**Essential Concepts:**
- Verification code is required for registration/login
- Categories organize products
- Products are core of commerce
- Basket is shopping cart before order
- Orders are created from basket
- Configurations store system settings

**Remember:**
- Always save authentication token after login/register
- Use token in `Authorization: Token {your-token}` header for authenticated requests
- Follow the dependency order when creating entities
- Check that basket has items before creating order

---

This guide provides the foundation for understanding and using the Zistino backend API system. Start with authentication, then follow the workflow step by step.

---

## Step 9: Addresses

### Why Addresses Are Required

Addresses store delivery locations for users. They are essential for:
- Order delivery (where to deliver products)
- Driver assignment (location-based zone matching)
- User convenience (saved addresses for quick checkout)
- Location tracking (latitude/longitude for mapping)

### Essential Fields

**Required:**
- `user` (foreign key) - Must link to existing User
- `address` (text) - Street address

**Optional but Recommended:**
- `full_name` (string) - Recipient name
- `phone_number` (string) - Contact phone for delivery
- `city` (string) - City name
- `province` (string) - Province/state name
- `country` (string) - Country name
- `zip_code` (string) - Postal code
- `latitude` (decimal) - GPS latitude (for driver assignment)
- `longitude` (decimal) - GPS longitude (for driver assignment)
- `description` (text) - Address label (e.g., "Home", "Work")
- `plate` (string) - Building plate number
- `unit` (string) - Unit/apartment number
- `email` (string) - Contact email
- `company_name` (string) - Company name (for business addresses)
- `company_number` (string) - Company registration number
- `vat_number` (string) - VAT/tax number

### How to Create

**Via Django Admin:**
1. Go to `Users` → `Addresses` → `Add Address`
2. Select user
3. Enter address details
4. Add latitude/longitude (optional but recommended for automatic driver assignment)
5. Save

**Via API:**
- `GET /api/v1/users/customer/addresses/` - List user's addresses
- `POST /api/v1/users/customer/addresses/` - Create new address
- `GET /api/v1/users/customer/addresses/{id}/` - Get address details
- `PUT /api/v1/users/customer/addresses/{id}/` - Update address
- `DELETE /api/v1/users/customer/addresses/{id}/` - Delete address

### Why Address Needs User

- Every address belongs to a user
- Users can have multiple addresses
- Addresses are used in orders for delivery location
- System uses address coordinates to find matching zone and assign driver

### Why Latitude/Longitude Matter

- **Automatic Zone Detection**: System finds which zone contains the address
- **Driver Assignment**: Drivers are assigned based on zone matching
- **Distance Calculation**: System calculates distance from zone center
- **Mapping**: Frontend apps display addresses on maps

---

## Step 10: Zones

### Why Zones Are Required

Zones are geographic areas used for:
- **Driver Assignment**: Drivers are assigned to orders based on zone
- **Service Area Management**: Define where service is available
- **Load Balancing**: Distribute orders evenly among drivers in a zone
- **Geographic Organization**: Organize deliveries by area

### Essential Fields

**Required:**
- `zone` (string) - Zone name (e.g., "North Tehran", "South Tehran")

**Optional but Recommended:**
- `center_latitude` (decimal) - Zone center point latitude
- `center_longitude` (decimal) - Zone center point longitude
- `radius_km` (decimal) - Zone radius in kilometers (default: 10.0)
- `description` (text) - Zone description
- `address` (text) - Zone address/area description
- `zonepath` (string) - Zone path identifier
- `is_active` (boolean) - Whether zone is active (default: true)

### How to Create

**Via Django Admin:**
1. Go to `Users` → `Zones` → `Add Zone`
2. Enter zone name
3. Set center latitude and longitude (required for automatic matching)
4. Set radius in kilometers
5. Add description
6. Set `is_active` to true
7. Save

**Via API:**
- `GET /api/v1/mapzone/` - List all zones
- `POST /api/v1/mapzone/` - Create new zone (Admin only)
- `GET /api/v1/mapzone/{id}/` - Get zone details
- `PUT /api/v1/mapzone/{id}/` - Update zone (Admin only)
- `DELETE /api/v1/mapzone/{id}/` - Delete zone (Admin only)
- `POST /api/v1/mapzone/search/` - Search zones
- `POST /api/v1/mapzone/createuserinzone/` - Assign user to zone (Admin only)
- `POST /api/v1/mapzone/userinzone/` - Get zones for a user (Admin only)
- `DELETE /api/v1/mapzone/userinzone/{id}/` - Remove user from zone (Admin only)
- `GET /api/v1/drivers/byzone/` - Get drivers in a zone (Admin only)

### Why Zones Need Center and Radius

- **Automatic Matching**: When order has latitude/longitude, system finds which zone contains it
- **Distance Calculation**: System calculates distance from zone center to order location
- **Driver Selection**: Drivers assigned to zones can be selected for orders in that zone
- **Service Coverage**: Radius defines service area for each zone

### User-Zone Relationship

- **UserZone Model**: Links users (especially drivers) to zones
- **Multiple Zones**: A user can be assigned to multiple zones
- **Driver Assignment**: Only drivers assigned to a zone can receive orders from that zone
- **Automatic Assignment**: When order is created with location, system finds matching zone and assigns driver from that zone

---

## Step 11: UserPoints

### Why UserPoints Are Required

UserPoints track user's points balance and lifetime statistics. Points are used for:
- **Rewards System**: Users earn points for orders and referrals
- **Lottery Participation**: Points can be spent on lottery tickets
- **Gamification**: Encourages user engagement and loyalty
- **Referral Incentives**: Rewards users for referring others

### Essential Fields

**Auto-created** when user first earns points. No manual creation needed.

**Fields:**
- `user` (OneToOne) - Links to User (one points account per user)
- `balance` (integer) - Current available points (default: 0)
- `lifetime_earned` (integer) - Total points earned in lifetime (default: 0)
- `lifetime_spent` (integer) - Total points spent in lifetime (default: 0)

### How Points Are Awarded

**Automatic Awards:**
- **Order Completion**: Points awarded when order status changes to "completed" (configured in `order_points` configuration)
- **Referral**: Points awarded when referred user completes first order (configured in `referral_points` configuration)
- **Welcome Bonus**: Points awarded on registration (if configured)

**Manual Awards (Admin only):**
- Admin can manually award points via admin panel or API

### How to Use

**Get Points Balance:**
- `GET /api/v1/points/my-balance/` - Get current user's points balance

**Get Points History:**
- `GET /api/v1/points/my-history/` - Get points transaction history (last 100 transactions)

**Admin Endpoints:**
- `POST /api/v1/points/search/` - Search point transactions (Admin only)
- `POST /api/v1/points/manual-award/` - Manually award points to user (Admin only)

### PointTransaction Model

Every points change is recorded in `PointTransaction`:
- `transaction_type`: "earned" or "spent"
- `source`: "order", "referral", "lottery", "manual", "welcome_bonus"
- `amount`: Points amount (positive for earned, represents deduction for spent)
- `reference_id`: Links to order/referral/lottery ID
- `balance_after`: User's balance after this transaction

### Why Points System Exists

- **Customer Retention**: Rewards encourage repeat orders
- **Referral Growth**: Incentivizes users to refer friends
- **Engagement**: Lottery system keeps users active
- **Loyalty**: Long-term customers accumulate more points

---

## Step 12: Wallet

### Why Wallet Is Required

Wallet stores user's money balance for:
- **Order Payments**: Users can pay for orders using wallet balance
- **Deposit System**: Users can deposit money to wallet
- **Refunds**: Money can be refunded to wallet
- **Payment Method**: Wallet is one of the payment methods (along with cash, card, etc.)

### Essential Fields

**Auto-created** when user first accesses wallet or makes transaction. No manual creation needed.

**Fields:**
- `user` (OneToOne) - Links to User (one wallet per user)
- `balance` (decimal) - Current wallet balance in Rials (default: 0.00)
- `created_at` (datetime) - When wallet was created
- `updated_at` (datetime) - Last update time

### How to Use

**Get Wallet Balance:**
- `GET /api/v1/payments/transactionwallet/mytransactionwallettotal` - Get current wallet balance

**Get Transaction History:**
- `GET /api/v1/payments/transactionwallet/mytransactionwallethistory` - Get transaction history (last 100 transactions)

**Get Credits/Receipts Report:**
- `GET /api/v1/payments/transactionwallet/my-report` - Get summary of total credits and receipts

**Admin Endpoints:**
- `POST /api/v1/transactionwallet/search/` - Search all transactions (Admin only)

### Why Wallet Exists

- **Convenience**: Users don't need to enter payment details every time
- **Prepaid System**: Users can deposit money and use it later
- **Transaction Tracking**: All wallet operations are recorded
- **Payment Flexibility**: Multiple payment methods including wallet

---

## Step 13: Transactions

### Why Transactions Are Required

Transactions record all wallet operations (credits and debits). They provide:
- **Audit Trail**: Complete history of all wallet operations
- **Transparency**: Users can see all their wallet activity
- **Accountability**: Every wallet change is recorded
- **Reference Tracking**: Transactions link to orders, deposits, refunds

### Essential Fields

**Required:**
- `wallet` (foreign key) - Must link to existing Wallet
- `amount` (decimal) - Transaction amount in Rials
- `transaction_type` (string) - "credit" (money added) or "debit" (money deducted)
- `status` (string) - "pending", "completed", "failed", "cancelled" (default: "pending")

**Optional:**
- `description` (text) - Transaction description
- `reference_id` (string) - Reference to order/deposit/refund ID

### Transaction Types

**Credit (Money Added):**
- Deposit requests (approved)
- Refunds from orders
- Manual admin credits

**Debit (Money Deducted):**
- Order payments
- Refunds to users
- Manual admin debits

### Transaction Status

- `pending`: Transaction created but not yet processed
- `completed`: Transaction successfully processed
- `failed`: Transaction failed (e.g., insufficient balance, payment gateway error)
- `cancelled`: Transaction was cancelled

### How Transactions Are Created

**Automatic:**
- When deposit request is approved → Credit transaction created
- When order is paid with wallet → Debit transaction created
- When refund is processed → Credit transaction created

**Manual (Admin only):**
- Admin can create transactions directly via admin panel

### How to Use

**Get Transaction History:**
- `GET /api/v1/payments/transactionwallet/mytransactionwallethistory` - Get user's transaction history

**Admin Endpoints:**
- `POST /api/v1/transactionwallet/search/` - Search all transactions (Admin only)

### Why Transactions Matter

- **Financial Records**: Complete audit trail of all money movements
- **User Trust**: Users can verify all wallet operations
- **Dispute Resolution**: Transactions provide evidence for disputes
- **Reporting**: Generate financial reports from transaction data

---

## Step 14: Deposits

### Why Deposits Are Required

Deposits allow users to add money to their wallet. This enables:
- **Prepaid System**: Users deposit money before making orders
- **Payment Flexibility**: Users can pay with wallet balance
- **Admin Verification**: Deposits require admin approval for security
- **SMS Notifications**: Users receive SMS when deposit is requested/approved

### Essential Fields

**Required:**
- `user` (foreign key) - Must link to existing User
- `amount` (decimal) - Amount to deposit in Rials (must be > 0)

**Optional:**
- `reference_id` (string) - Bank receipt or reference number
- `description` (text) - Additional notes or description
- `status` (string) - "pending", "approved", "rejected", "cancelled" (default: "pending")
- `verified_at` (datetime) - When admin verified the deposit
- `verified_by` (foreign key) - Admin user who verified
- `transaction` (OneToOne) - Transaction created when approved

### Deposit Status Flow

1. **Pending**: User creates deposit request → Status: "pending"
2. **Approved**: Admin approves → Status: "approved", wallet balance increased, transaction created, SMS sent
3. **Rejected**: Admin rejects → Status: "rejected", SMS sent
4. **Cancelled**: User or system cancels → Status: "cancelled"

### How to Use

**Customer Endpoints:**
- `POST /api/v1/payments/deposits/request/` - Create deposit request (SMS sent automatically)
- `GET /api/v1/payments/deposits/my-requests/` - List user's deposit requests
- `GET /api/v1/payments/deposits/my-requests/{id}/` - Get deposit request details

**Admin Endpoints:**
- `POST /api/v1/payments/deposits/search/` - Search deposit requests (Admin only)
- `POST /api/v1/payments/deposits/{id}/approve/` - Approve deposit request (Admin only, creates transaction, updates wallet, sends SMS)
- `POST /api/v1/payments/deposits/{id}/reject/` - Reject deposit request (Admin only, sends SMS)

### What Happens When Deposit Is Approved

1. **Transaction Created**: Credit transaction created with amount
2. **Wallet Updated**: User's wallet balance increased by amount
3. **Status Updated**: Deposit request status changed to "approved"
4. **SMS Sent**: Confirmation SMS sent to user
5. **Reference Linked**: Transaction linked to deposit request

### Why Deposits Need Admin Approval

- **Security**: Prevents fraudulent deposits
- **Verification**: Admin verifies bank receipt/reference
- **Control**: Ensures only legitimate deposits are processed
- **Audit**: Admin approval creates audit trail

### Testing Deposit Request and Transaction Flow

**Complete testing workflow to verify deposits, transactions, and SMS:**

#### Prerequisites

1. **SMS Configuration** - Ensure SMS credentials are configured in `.env`:
   ```env
   MIZBAN_SMS_AUTH_TOKEN=your_auth_token
   MIZBAN_SMS_SENDER=5000467254
   MIZBAN_SMS_API_URL=https://services.mizbansms.com/api/Message/SendMessage
   ```
2. **Authentication Token** - Have valid user token for customer and admin token for approval
3. **Restart Django** - After updating `.env`, restart Django server

#### Step 1: Test SMS Service (Optional but Recommended)

**Before testing deposits, verify SMS is working:**

**Endpoint**: `POST /api/v1/payments/test-sms/` (Admin only)

**Request:**
```json
{
  "phoneNumber": "09056761466",
  "message": "Test SMS from Django backend"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "SMS sent successfully",
  "phoneNumber": "09056761466",
  "sentMessage": "Test SMS from Django backend",
  "note": "Check the phone for received SMS"
}
```

**If SMS works:** Continue to Step 2  
**If SMS fails:** Check `.env` file and Django logs, fix SMS configuration first

#### Step 2: Create Deposit Request (Customer)

**Endpoint**: `POST /api/v1/payments/deposits/request/`

**Headers:**
```
Authorization: Token your-customer-token-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "amount": 100000
}
```

**What Happens:**
1. Deposit request created with status "pending"
2. SMS sent automatically: "Your deposit request of 100,000 Rials has been registered. Please deposit the money and wait for verification."
3. Check your phone for SMS confirmation

**Expected Response:**
```json
{
  "id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "amount": "100000.00",
  "status": "pending",
  "reference_id": "",
  "createdAt": "2025-01-15T10:30:00Z"
}
```

**Verify:**
- ✅ Deposit request created successfully
- ✅ Status is "pending"
- ✅ SMS received on phone

#### Step 3: View Deposit Requests (Customer)

**Endpoint**: `GET /api/v1/payments/deposits/my-requests/`

**Headers:**
```
Authorization: Token your-customer-token-here
```

**Expected Response:**
```json
[
  {
    "id": "46e818ce-0518-4c64-8438-27bc7163a706",
    "amount": "100000.00",
    "status": "pending",
    "createdAt": "2025-01-15T10:30:00Z"
  }
]
```

**Verify:**
- ✅ Deposit request appears in list
- ✅ Status is "pending"

#### Step 4: Approve Deposit Request (Admin)

**Endpoint**: `POST /api/v1/payments/deposits/{deposit_id}/approve/`

**Headers:**
```
Authorization: Token your-admin-token-here
Content-Type: application/json
```

**Request Body (Optional):**
```json
{
  "reference_id": "BANK-RECEIPT-12345"
}
```

**What Happens:**
1. Deposit request status changed to "approved"
2. **Transaction created** (credit type, status: completed)
3. **Wallet balance increased** by deposit amount
4. **SMS sent automatically**: "{amount} Rials have been deposited into your account. Your current balance is {balance} Rials."
5. Check your phone for SMS confirmation

**Expected Response:**
```json
{
  "id": "46e818ce-0518-4c64-8438-27bc7163a706",
  "status": "approved",
  "wallet_balance": "100000.00",
  "transaction_id": "0641067f-df76-416c-98cd-6f89e43d3b3f"
}
```

**Verify:**
- ✅ Deposit request status is "approved"
- ✅ Wallet balance increased
- ✅ Transaction created
- ✅ SMS received on phone

#### Step 5: Verify Wallet Balance (Customer)

**Endpoint**: `GET /api/v1/payments/transactionwallet/mytransactionwallettotal`

**Headers:**
```
Authorization: Token your-customer-token-here
```

**Expected Response:**
```json
{
  "total": "100000.00"
}
```

**Verify:**
- ✅ Wallet balance matches deposit amount

#### Step 6: Verify Transaction History (Customer)

**Endpoint**: `GET /api/v1/payments/transactionwallet/mytransactionwallethistory`

**Headers:**
```
Authorization: Token your-customer-token-here
```

**Expected Response:**
```json
[
  {
    "id": "0641067f-df76-416c-98cd-6f89e43d3b3f",
    "amount": "100000.00",
    "transaction_type": "credit",
    "status": "completed",
    "description": "Deposit request 46e818ce-0518-4c64-8438-27bc7163a706",
    "reference_id": "BANK-RECEIPT-12345",
    "created_at": "2025-01-15T11:00:00Z"
  }
]
```

**Verify:**
- ✅ Transaction appears in history
- ✅ Transaction type is "credit"
- ✅ Status is "completed"
- ✅ Amount matches deposit amount

#### Step 7: Verify Transaction Created (Admin)

**Endpoint**: `POST /api/v1/transactionwallet/search/` (Admin only)

**Headers:**
```
Authorization: Token your-admin-token-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "pageNumber": 1,
  "pageSize": 20,
  "keyword": "",
  "advancedSearch": {
    "fields": ["userid"],
    "keyword": "customer-user-id-here"
  }
}
```

**Verify:**
- ✅ Transaction exists in database
- ✅ Transaction linked to correct user
- ✅ Transaction linked to deposit request

### Complete Testing Checklist

**Before Testing:**
- [ ] SMS credentials configured in `.env`
- [ ] Django server restarted after updating `.env`
- [ ] Test SMS endpoint works (SMS received)
- [ ] Have valid customer authentication token
- [ ] Have valid admin authentication token (is_staff=True)

**During Testing:**
- [ ] Create deposit request → SMS received
- [ ] Deposit request appears in list (status: pending)
- [ ] Approve deposit request → SMS received
- [ ] Wallet balance increased
- [ ] Transaction created in history
- [ ] Transaction visible in admin search

**After Testing:**
- [ ] Verify all SMS received
- [ ] Verify wallet balance is correct
- [ ] Verify transaction records are correct
- [ ] Check Django logs for any errors

### Troubleshooting

**SMS Not Received:**
1. Check `.env` file has `MIZBAN_SMS_AUTH_TOKEN`
2. Test SMS endpoint first: `POST /api/v1/payments/test-sms/`
3. Check Django console for SMS errors
4. Verify phone number format is correct
5. Check Mizban SMS account balance

**Deposit Request Created But No SMS:**
- Check Django logs for SMS error
- Verify SMS service is working (test endpoint)
- SMS errors don't fail deposit request (logged only)

**Transaction Not Created After Approval:**
- Check Django logs for errors
- Verify admin token has is_staff=True
- Check wallet was created for user
- Verify deposit request status changed to "approved"

---

## Step 15: SMS

### Why SMS Is Required

SMS notifications keep users informed about:
- **Verification Codes**: Sent during registration/login
- **Order Updates**: Order confirmation, status changes, delivery reminders
- **Deposit Notifications**: Deposit request confirmation, approval, rejection
- **System Alerts**: Important account or system notifications

### How SMS Works

**SMS Service:**
- Located in: `zistino_apps/payments/sms_service.py`
- Uses Mizban SMS API for sending
- Configured via `.env` file (MIZBAN_SMS_USERNAME, MIZBAN_SMS_PASSWORD, etc.)
- Falls back to console logging if credentials not configured (development mode)

### SMS Functions

**Basic Function:**
- `send_sms(phone_number, message)` - Send any SMS message

**Pre-built Functions:**
- `send_deposit_request_confirmation(phone_number, amount)` - Deposit request confirmation
- `send_deposit_confirmation(phone_number, amount)` - Deposit approval confirmation
- `send_deposit_rejection(phone_number, amount)` - Deposit rejection notification

### How SMS Is Used

**Automatic SMS:**
- **Verification Codes**: Sent when user requests code (via `send-code` endpoint)
- **Deposit Requests**: Sent when user creates deposit request
- **Deposit Approval**: Sent when admin approves deposit
- **Deposit Rejection**: Sent when admin rejects deposit
- **Delivery Reminders**: Sent 1 hour before delivery (if configured)

**Manual SMS (Admin):**
- Admin can send custom SMS via admin panel or API

### SMS Configuration

**Required Environment Variables:**
- `MIZBAN_SMS_USERNAME` - Mizban SMS username
- `MIZBAN_SMS_PASSWORD` - Mizban SMS password
- `MIZBAN_SMS_API_URL` - API endpoint (default: https://services.mizbansms.com/api/Message/SendMessage)
- `MIZBAN_SMS_SENDER` - Sender phone number
- `MIZBAN_SMS_AUTH_TOKEN` - Authentication token (if required)

### Testing SMS

**Test Endpoint (Admin only):**
- `POST /api/v1/payments/test-sms/` - Send test SMS to verify integration

**Request Body:**
```json
{
  "phoneNumber": "09123456789",
  "message": "Test message (optional)"
}
```

### Why SMS Matters

- **User Engagement**: Users stay informed about their orders and account
- **Security**: Verification codes prevent unauthorized access
- **Trust**: Notifications build user confidence
- **Communication**: Direct channel to reach users

### SMS Best Practices

- **Non-blocking**: SMS failures don't break API responses
- **Error Handling**: SMS errors are logged but don't fail the operation
- **Development Mode**: In development, SMS is logged to console if credentials not configured
- **Rate Limiting**: Be mindful of SMS API rate limits
- **Message Length**: Keep messages concise (SMS has character limits)

---

## Additional API Endpoints Reference

### Addresses
- `GET /api/v1/users/customer/addresses/` - List user's addresses
- `POST /api/v1/users/customer/addresses/` - Create address
- `GET /api/v1/users/customer/addresses/{id}/` - Get address details
- `PUT /api/v1/users/customer/addresses/{id}/` - Update address
- `DELETE /api/v1/users/customer/addresses/{id}/` - Delete address

### Zones
- `GET /api/v1/mapzone/` - List zones
- `POST /api/v1/mapzone/` - Create zone (Admin only)
- `GET /api/v1/mapzone/{id}/` - Get zone details
- `PUT /api/v1/mapzone/{id}/` - Update zone (Admin only)
- `DELETE /api/v1/mapzone/{id}/` - Delete zone (Admin only)
- `POST /api/v1/mapzone/search/` - Search zones
- `POST /api/v1/mapzone/createuserinzone/` - Assign user to zone (Admin only)
- `POST /api/v1/mapzone/userinzone/` - Get zones for user (Admin only)
- `DELETE /api/v1/mapzone/userinzone/{id}/` - Remove user from zone (Admin only)
- `GET /api/v1/drivers/byzone/` - Get drivers in zone (Admin only)

### UserPoints
- `GET /api/v1/points/my-balance/` - Get points balance
- `GET /api/v1/points/my-history/` - Get points history
- `POST /api/v1/points/search/` - Search point transactions (Admin only)
- `POST /api/v1/points/manual-award/` - Manually award points (Admin only)

### Wallet
- `GET /api/v1/payments/transactionwallet/mytransactionwallettotal` - Get wallet balance
- `GET /api/v1/payments/transactionwallet/mytransactionwallethistory` - Get transaction history
- `GET /api/v1/payments/transactionwallet/my-report` - Get credits/receipts report
- `POST /api/v1/transactionwallet/search/` - Search transactions (Admin only)

### Deposits
- `POST /api/v1/payments/deposits/request/` - Create deposit request
- `GET /api/v1/payments/deposits/my-requests/` - List user's deposit requests
- `GET /api/v1/payments/deposits/my-requests/{id}/` - Get deposit request details
- `POST /api/v1/payments/deposits/search/` - Search deposit requests (Admin only)
- `POST /api/v1/payments/deposits/{id}/approve/` - Approve deposit (Admin only)
- `POST /api/v1/payments/deposits/{id}/reject/` - Reject deposit (Admin only)

### SMS
- `POST /api/v1/payments/test-sms/` - Test SMS sending (Admin only)

---

## Complete System Overview

### Entity Relationships

```
User
├── Address (one-to-many)
├── Wallet (one-to-one)
├── UserPoints (one-to-one)
├── UserZone (many-to-many via UserZone)
├── Basket (one-to-one)
├── Orders (one-to-many)
└── DepositRequests (one-to-many)

Zone
├── UserZone (many-to-many via UserZone)
└── Deliveries (via orders in zone)

Wallet
└── Transactions (one-to-many)

UserPoints
└── PointTransactions (one-to-many)

DepositRequest
└── Transaction (one-to-one, when approved)
```

### Complete Workflow with All Features

1. **Authentication**
   - Send verification code → Receive SMS
   - Register/Login → Get token

2. **Profile Setup**
   - Get/Update profile
   - Add addresses (with latitude/longitude)
   - Upload profile image

3. **Points & Referrals**
   - Get points balance
   - Get referral code
   - Share referral code
   - Earn points from orders/referrals

4. **Wallet & Deposits**
   - Create deposit request → Receive SMS
   - Admin approves → Wallet balance increased → Receive SMS
   - Get wallet balance
   - View transaction history

5. **Products & Orders**
   - Browse categories and products
   - Add to basket
   - Create order (with address/location)
   - System finds zone → Assigns driver → Sends SMS

6. **Zones & Drivers**
   - Admin creates zones (with center/radius)
   - Admin assigns drivers to zones
   - System automatically matches orders to zones
   - Drivers receive orders from their zones

---

This comprehensive guide covers all major components of the Zistino backend API system. Use it as a reference when building features or troubleshooting issues.

