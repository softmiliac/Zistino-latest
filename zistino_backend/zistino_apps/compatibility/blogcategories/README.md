# BlogCategories Compatibility Endpoints

This folder contains compatibility routes for the BlogCategories API endpoints.

## Structure

- `__init__.py` - Module initialization
- `urls.py` - All 9 blogcategories endpoints from Flutter Swagger
- `views.py` - Views using existing BlogCategory model
- `README.md` - This file

## Endpoints

All 9 endpoints from Swagger UI: https://recycle.metadatads.com/swagger/index.html#/BlogCategories

### Standard REST Endpoints (3):
1. **GET** `/api/v1/blogcategories/{id}` → `BlogCategoriesDetailView.get()` - Retrieves a blog category by its ID
2. **PUT** `/api/v1/blogcategories/{id}` → `BlogCategoriesDetailView.put()` - Updates an existing blog category by its ID
3. **DELETE** `/api/v1/blogcategories/{id}` → `BlogCategoriesDetailView.delete()` - Deletes a blog category by its ID
4. **POST** `/api/v1/blogcategories` → `BlogCategoriesListView.post()` - Creates a new blog category

### Special Endpoints (5):
5. **GET** `/api/v1/blogcategories/dapper` → `BlogCategoriesDapperView.get()` - Get blog categories (dapper context)
6. **POST** `/api/v1/blogcategories/search` → `BlogCategoriesSearchView.post()` - Search blog categories using available Filters
7. **GET** `/api/v1/blogcategories/all` → `BlogCategoriesAllView.get()` - Retrieves all blog categories
8. **GET** `/api/v1/blogcategories/client/all` → `BlogCategoriesClientAllView.get()` - Retrieves all blog categories for client-side use
9. **GET** `/api/v1/blogcategories/client/categories` → `BlogCategoriesClientCategoriesView.get()` - Retrieves categories for client-side use

## Status

✅ **Fully Implemented**: Uses existing `BlogCategory` model from `zistino_apps.content.models`

## Implementation Details

- **Model**: Uses existing `BlogCategory` model (no new model needed)
- **Serializer**: Uses existing `BlogCategorySerializer`
- **ViewSet**: Wraps existing `BlogCategoryViewSet` from `content.views`
- **Permissions**: 
  - GET endpoints: `AllowAny` (public)
  - POST/PUT/DELETE: `IsAuthenticated` + `IsManager` (admin only)
- **Swagger Tag**: All endpoints tagged with `'BlogCategories'` to appear grouped in Swagger UI

## Source

Endpoints are based on Flutter Swagger documentation:
https://recycle.metadatads.com/swagger/index.html#/BlogCategories

## Usage

This route is automatically included in the main compatibility URLs via:
```python
path('blogcategories/', include('zistino_apps.compatibility.blogcategories.urls'))
```

