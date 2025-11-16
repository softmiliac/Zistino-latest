"""
MailTemplates compatibility URL routes for Flutter apps.
All 7 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/MailTemplates

Flutter expects: /api/v1/mailtemplates/{endpoint}
All endpoints are tagged with 'MailTemplates' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/mailtemplates/{id} - Retrieves a mail template by its ID
2. PUT /api/v1/mailtemplates/{id} - Updates an existing mail template by its ID
3. DELETE /api/v1/mailtemplates/{id} - Deletes a mail template by its ID
4. GET /api/v1/mailtemplates/dapper - Get mail templates (dapper context)
5. POST /api/v1/mailtemplates/search - Search MailTemplates using available Filters
6. POST /api/v1/mailtemplates - Creates a new mail template
7. GET /api/v1/mailtemplates/all - Retrieves all mail templates
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.MailTemplateViewSet, basename='mailtemplate')

urlpatterns = [
    # STANDARD REST ENDPOINTS (via router)
    path('', include(router.urls)),
]

