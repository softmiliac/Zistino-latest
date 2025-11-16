# AdsItems Compatibility Endpoints

This folder contains all compatibility routes for the AdsItems API endpoints.

## Structure

- `__init__.py` - Module initialization
- `urls.py` - All 7 adsitems endpoints from Flutter Swagger
- `views.py` - Placeholder views (to be implemented)
- `README.md` - This file

## Endpoints

All 7 endpoints from Swagger UI:

### Standard REST (4 endpoints)
- `GET /api/v1/adsitems/` → `AdsItemsViewSet.list()` (to be implemented)
- `POST /api/v1/adsitems/` → `AdsItemsViewSet.create()` (to be implemented)
- `GET /api/v1/adsitems/{id}/` → `AdsItemsViewSet.retrieve()` (to be implemented)
- `PUT /api/v1/adsitems/{id}/` → `AdsItemsViewSet.update()` (to be implemented)
- `DELETE /api/v1/adsitems/{id}/` → `AdsItemsViewSet.destroy()` (to be implemented)

### Special Endpoints (2 endpoints)
- `GET /api/v1/adsitems/dapper` → `AdsItemsViewSet.dapper()` (to be implemented)
- `POST /api/v1/adsitems/search` → `AdsItemsViewSet.search()` (to be implemented)
  - Description: "Search AdsItems using available Filters."

### Client Endpoints (1 endpoint)
- `GET /api/v1/adsitems/client/by-zoneid/{id}/` → `AdsItemsViewSet.client_by_zoneid()` (to be implemented)

## Status

⚠️ **Currently Placeholder**: The AdsItem functionality is not yet implemented in the backend. All endpoints return `501 NOT_IMPLEMENTED` status.

## Next Steps

1. Create `AdsItem` model in appropriate app (likely `content` or new `ads` app)
2. Create `AdsItemSerializer`
3. Implement the views in `views.py`
4. Update permissions as needed
5. Test all endpoints

## Source

All endpoints are based on Flutter Swagger documentation:
https://recycle.metadatads.com/swagger/index.html#/AdsItems

## Usage

These routes are automatically included in the main compatibility URLs via:
```python
path('adsitems/', include('zistino_apps.compatibility.adsitems.urls'))
```

