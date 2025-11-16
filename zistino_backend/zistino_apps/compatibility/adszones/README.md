# AdsZones Compatibility Endpoints

This folder contains all compatibility routes for the AdsZones API endpoints.

## Structure

- `__init__.py` - Module initialization
- `urls.py` - All 7 adszones endpoints from Flutter Swagger
- `views.py` - Placeholder views (to be implemented)
- `README.md` - This file

## Endpoints

All 7 endpoints from Swagger UI:

### Standard REST (5 endpoints)
- `GET /api/v1/adszones/` → `AdsZonesViewSet.list()` (to be implemented)
- `POST /api/v1/adszones/` → `AdsZonesViewSet.create()` (to be implemented)
- `GET /api/v1/adszones/{id}/` → `AdsZonesViewSet.retrieve()` (to be implemented)
- `PUT /api/v1/adszones/{id}/` → `AdsZonesViewSet.update()` (to be implemented)
- `DELETE /api/v1/adszones/{id}/` → `AdsZonesViewSet.destroy()` (to be implemented)

### Special Endpoints (2 endpoints)
- `GET /api/v1/adszones/dapper` → `AdsZonesViewSet.dapper()` (to be implemented)
- `POST /api/v1/adszones/search` → `AdsZonesViewSet.search()` (to be implemented)
  - Description: "Search AdsZones using available Filters."
- `GET /api/v1/adszones/all` → `AdsZonesViewSet.all()` (to be implemented)

## Status

⚠️ **Currently Placeholder**: The AdsZone functionality is not yet implemented in the backend. All endpoints return `501 NOT_IMPLEMENTED` status.

## Next Steps

1. Create `AdsZone` model in appropriate app (likely `content` or new `ads` app)
2. Create `AdsZoneSerializer`
3. Implement the views in `views.py`
4. Update permissions as needed
5. Test all endpoints

## Source

All endpoints are based on Flutter Swagger documentation:
https://recycle.metadatads.com/swagger/index.html#/AdsZones

## Usage

These routes are automatically included in the main compatibility URLs via:
```python
path('adszones/', include('zistino_apps.compatibility.adszones.urls'))
```

