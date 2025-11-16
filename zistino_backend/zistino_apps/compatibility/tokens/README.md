# Tokens Compatibility Layer

## ✅ What Was Done

Updated the `POST /api/v1/tokens` endpoint to match the **exact format** from the old Swagger API.

### Changes Made:

1. **Response Wrapper**: All responses now use the wrapper format:
   ```json
   {
     "data": {
       "token": "...",
       "refreshToken": "...",
       "refreshTokenExpiryTime": "2026-01-06T15:08:35.9672227Z"
     },
     "messages": [],
     "succeeded": true
   }
   ```

2. **Tenant Header**: Tenant is now read from the `tenant` header (not body):
   - Header: `tenant: root`
   - Request body: `{ "email": "...", "password": "..." }`

3. **JWT Tokens**: Implemented JWT token generation matching old Swagger format
   - Uses PyJWT library (with fallback to DRF Token if not installed)
   - JWT payload includes all claims from old Swagger

4. **Refresh Tokens**: Created `RefreshToken` model to store refresh tokens
   - 30-day expiry
   - Supports token refresh endpoint

5. **Error Responses**: Error responses match old Swagger format:
   - 400 errors: `{ "type": "...", "title": "...", "status": 400, "detail": "...", "errors": {...} }`
   - Other errors: `{ "messages": [...], "succeeded": false, "exception": "...", "statusCode": ... }`

## 📋 Next Steps

### 1. Install PyJWT (Recommended)
```bash
pip install PyJWT
```

This will enable JWT token generation matching the old Swagger format exactly.

### 2. Run Migrations
```bash
python manage.py makemigrations compatibility.tokens
python manage.py migrate
```

This will create the `refresh_tokens` table.

### 3. Test the Endpoint

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/tokens' \
  -H 'accept: application/json' \
  -H 'tenant: root' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "admin@root.com",
    "password": "123Pa$$word!"
  }'
```

**Expected Response (200):**
```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "4nUZ22tidpRInaFq3BJNoGNcin89um4uATArr7wdSz0=",
    "refreshTokenExpiryTime": "2026-01-06T15:08:35.9672227Z"
  },
  "messages": [],
  "succeeded": true
}
```

## 🔍 What Matches Old Swagger

✅ Request body format: `{ "email": "...", "password": "..." }`  
✅ Tenant header: `tenant: root`  
✅ Response wrapper: `{ "data": {...}, "messages": [], "succeeded": true }`  
✅ Token format: JWT token (if PyJWT installed)  
✅ Refresh token: Random string with expiry time  
✅ Error responses: Match old Swagger format exactly  

## 📝 Notes

- If PyJWT is not installed, the system falls back to DRF Token (simpler format, but still works)
- Refresh tokens are stored in the database and can be revoked
- JWT tokens expire after 7 days
- Refresh tokens expire after 30 days

## 🚀 Other Endpoints

All other token endpoints (`tokenbyemail`, `token-by-code`, `refresh`, etc.) have been updated with the same response wrapper format.

