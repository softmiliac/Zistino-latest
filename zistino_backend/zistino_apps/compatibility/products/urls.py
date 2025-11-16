"""
URL patterns for Products compatibility layer.
Provides all ~34 endpoints matching Flutter app expectations.
"""
from django.urls import path, include
from ..router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
router.register(r'', views.ProductsViewSet, basename='products')

urlpatterns = [
    # IMPORTANT: Custom endpoints must come BEFORE router URLs to avoid conflicts
    # Router will try to match everything as {id} UUID, so specific paths must come first
    
    # Custom endpoints - Image 1
    path('edit/<str:id>', views.ProductsEditView.as_view(), name='products-edit'),
    path('dapper/<str:id>', views.ProductsDapperView.as_view(), name='products-dapper'),
    path('all', views.ProductsAllView.as_view(), name='products-all'),
    
    # Client endpoints (must come before router to avoid UUID validation conflicts)
    path('client', views.ProductsClientView.as_view(), name='products-client-create'),
    path('client/by-name', views.ProductsClientByNameView.as_view(), name='products-client-by-name'),
    path('client/top5', views.ProductsClientTop5View.as_view(), name='products-client-top5'),
    path('client/search', views.ProductsClientSearchView.as_view(), name='products-client-search'),
    path('client/searchext', views.ProductsClientSearchExtView.as_view(), name='products-client-searchext'),
    path('client/searchwithtags', views.ProductsClientSearchWithTagsView.as_view(), name='products-client-searchwithtags'),
    path('client/bytagname', views.ProductsClientByTagNameView.as_view(), name='products-client-bytagname'),
    path('client/by-categoryid/top5/<str:id>', views.ProductsClientByCategoryIdTop5View.as_view(), name='products-client-by-categoryid-top5'),
    path('client/by-categorytype/top5/<str:id>', views.ProductsClientByCategoryTypeTop5View.as_view(), name='products-client-by-categorytype-top5'),
    path('client/by-categoryid/<str:id>', views.ProductsClientByCategoryIdView.as_view(), name='products-client-by-categoryid'),
    path('client/by-categorytype/<str:id>', views.ProductsClientByCategoryTypeView.as_view(), name='products-client-by-categorytype'),
    path('client/withrelatedbycategory/<str:id>', views.ProductsClientWithRelatedByCategoryView.as_view(), name='products-client-withrelatedbycategory'),
    path('client/prefilter/<str:id>', views.ProductsClientPrefilterView.as_view(), name='products-client-prefilter'),
    path('client/prefiltermaxmin/<str:Name>', views.ProductsClientPrefilterMaxMinView.as_view(), name='products-client-prefiltermaxmin'),
    path('client/filter/<str:type>/<str:name>', views.ProductsClientFilterByTypeView.as_view(), name='products-client-filter-by-type'),
    path('client/filter/<str:name>', views.ProductsClientFilterView.as_view(), name='products-client-filter'),
    path('client/<str:id>', views.ProductsClientRetrieveView.as_view(), name='products-client-retrieve'),
    
    # Custom endpoints - Image 2
    path('sold/<str:productId>', views.ProductsSoldView.as_view(), name='products-sold'),
    
    # Admin endpoints
    path('admin/searchext', views.ProductsAdminSearchExtView.as_view(), name='products-admin-searchext'),
    
    # Router URLs (handles: GET/POST /api/v1/products, GET/PUT/DELETE /api/v1/products/{id})
    # Must come LAST to avoid catching custom endpoints
    path('', include(router.urls)),
]

