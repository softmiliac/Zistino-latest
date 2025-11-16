# Addresses Compatibility Endpoints

This folder contains all compatibility routes for the Addresses API endpoints.

## Structure

- `__init__.py` - Module initialization
- `urls.py` - All 11 addresses endpoints from Flutter Swagger
- `README.md` - This file

## Endpoints

All endpoints are mapped from Flutter's expected format to backend viewsets:

### Standard REST (6 endpoints)
- `GET /api/v1/addresses/` → `AddressViewSet.list()`
- `POST /api/v1/addresses/` → `AddressViewSet.create()`
- `GET /api/v1/addresses/{id}/` → `AddressViewSet.retrieve()`
- `PUT /api/v1/addresses/{id}/` → `AddressViewSet.update()`
- `PATCH /api/v1/addresses/{id}/` → `AddressViewSet.partial_update()`
- `DELETE /api/v1/addresses/{id}/` → `AddressViewSet.destroy()`

### Custom Endpoints (5 endpoints)
- `GET /api/v1/addresses/by-userid` → `AddressViewSet.list()`
- `GET /api/v1/addresses/client/by-userid` → `CustomerAddressViewSet.list()`
- `POST /api/v1/addresses/client` → `CustomerAddressViewSet.create()`
- `PUT /api/v1/addresses/client/{id}/` → `CustomerAddressViewSet.update()`
- `DELETE /api/v1/addresses/client/{id}/` → `CustomerAddressViewSet.destroy()`

### Special Endpoints (2 endpoints)
- `GET /api/v1/addresses/dapper` → `AddressViewSet.list()` (may need custom view)
- `POST /api/v1/addresses/search` → `AddressViewSet.list()` (may need custom search view)

## Source

All endpoints are based on Flutter Swagger documentation:
https://recycle.metadatads.com/swagger/index.html#/Addresses

## Usage

These routes are automatically included in the main compatibility URLs via:
```python
path('addresses/', include('zistino_apps.compatibility.addresses.urls'))
```

