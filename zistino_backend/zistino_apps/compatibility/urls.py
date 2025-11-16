"""
Compatibility URL routes for Flutter apps.
These routes map old endpoint patterns to new backend views for backward compatibility.

Flutter apps use pattern: /api/v1/{controller}/{endpoint}
Backend uses pattern: /api/v1/{app}/{endpoint}/

This file bridges the gap by providing both patterns.
"""
from django.urls import path, include
from zistino_apps.authentication import views as auth_views
from zistino_apps.users import views as users_views
from zistino_apps.deliveries import views as deliveries_views
from zistino_apps.payments import views as payments_views
from zistino_apps.products import views as products_views
from zistino_apps.orders import views as orders_views
from zistino_apps.baskets import views as baskets_views
from . import views as compatibility_views

urlpatterns = [
    # ============================================================================
    # IDENTITY CONTROLLER COMPATIBILITY ROUTES
    # Flutter expects: /api/v1/identity/{endpoint}
    # ============================================================================
    
    # Registration
    # Flutter: /api/v1/identity/register-with-code
    # Backend: /api/v1/auth/register/
    path('identity/register-with-code', auth_views.RegisterView.as_view(), name='identity-register'),
    
    # Password Reset
    # Flutter: /api/v1/identity/forgot-password-by-code
    # Backend: /api/v1/auth/forgot-password/
    path('identity/forgot-password-by-code', auth_views.ForgotPasswordView.as_view(), name='identity-forgot-password'),
    
    # Flutter: /api/v1/identity/reset-password-by-code
    # Backend: /api/v1/auth/reset-password/
    path('identity/reset-password-by-code', auth_views.ResetPasswordView.as_view(), name='identity-reset-password'),
    
    # Flutter: /api/v1/identity/check-reset-password-code
    # Backend: /api/v1/auth/verify-code/ (or create specific view)
    path('identity/check-reset-password-code', auth_views.VerifyCodeView.as_view(), name='identity-check-reset-code'),
    
    # ============================================================================
    # TOKENS CONTROLLER COMPATIBILITY ROUTES
    # Flutter expects: /api/v1/tokens/{endpoint}
    # ============================================================================
    
    # Login/Token
    # Flutter: /api/v1/tokens/token-by-code (already exists in auth/urls.py)
    # Flutter: /api/v1/tokens/tokenbycode (alternative name)
    # Backend: /api/v1/auth/login/
    path('tokens/tokenbycode', auth_views.LoginView.as_view(), name='tokens-login-alias'),
    
    # Send Code
    # Flutter: /api/v1/tokens/send-code?phoneNumber=...
    # Backend: /api/v1/auth/send-code/
    path('tokens/send-code', auth_views.SendCodeView.as_view(), name='tokens-send-code-compat'),
    
    # ============================================================================
    # DRIVERDELIVERY CONTROLLER COMPATIBILITY ROUTES
    # Flutter expects: /api/v1/driverdelivery/{endpoint}
    # ============================================================================
    
    # Note: driverdelivery routes are now in compatibility/driverdelivery/ folder
    
    # Followup (already exists in main urls.py as driverdelivery/followup)
    # Flutter: /api/v1/driverdelivery/followup
    # Backend: /api/v1/driverdelivery/followup (already exists!)
    # No need to add here, it's already in main urls.py
    
    # Search
    # Flutter: /api/v1/driverdelivery/search
    # Backend: /api/v1/driverdelivery/search (already exists in main urls.py)
    # No need to add here
    
    # ============================================================================
    # PERSONAL CONTROLLER COMPATIBILITY ROUTES
    # Flutter expects: /api/v1/personal/{endpoint}
    # ============================================================================
    # TRANSACTIONWALLET CONTROLLER COMPATIBILITY ROUTES
    # Flutter expects: /api/v1/transactionwallet/{endpoint}
    # ============================================================================
    
    # My Transaction Wallet Total
    # Flutter: /api/v1/transactionwallet/mytransactionwallettotal
    # Backend: /api/v1/payments/transactionwallet/mytransactionwallettotal (already exists!)
    # Note: This is already mapped in payments/urls.py, but we can add alias here if needed
    # path('transactionwallet/mytransactionwallettotal', payments_views.WalletViewSet.as_view({'get': 'my_total'}), name='transactionwallet-total-compat'),
    
    # My Transaction Wallet History
    # Flutter: /api/v1/transactionwallet/mytransactionwallethistory
    # Backend: /api/v1/payments/transactionwallet/mytransactionwallethistory (already exists!)
    # path('transactionwallet/mytransactionwallethistory', payments_views.TransactionViewSet.as_view({'get': 'my_history'}), name='transactionwallet-history-compat'),
    
    # ============================================================================
    # ORDERS CONTROLLER COMPATIBILITY ROUTES
    # Flutter expects: /api/v1/orders/{endpoint}
    # ============================================================================
    
    # Client Search (for orders)
    # Flutter: /api/v1/orders/client/search
    # Backend: /api/v1/orders/customer/orders/client/search/
    path('orders/client/search', orders_views.CustomerOrdersViewSet.as_view({'post': 'client_search'}), name='orders-client-search-compat'),
    
    # ============================================================================
    # ADDRESSES CONTROLLER COMPATIBILITY ROUTES
    # All 11 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Addresses
    # Organized in separate addresses/ folder
    # ============================================================================
    path('addresses/', include('zistino_apps.compatibility.addresses.urls')),
    
    # ============================================================================
    # ADSITEMS CONTROLLER COMPATIBILITY ROUTES
    # All 7 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/AdsItems
    # Organized in separate adsitems/ folder
    # ============================================================================
    path('adsitems/', include('zistino_apps.compatibility.adsitems.urls')),
    
    # ============================================================================
    # ADSZONES CONTROLLER COMPATIBILITY ROUTES
    # All 7 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/AdsZones
    # Organized in separate adszones/ folder
    # ============================================================================
    path('adszones/', include('zistino_apps.compatibility.adszones.urls')),
    
    # ============================================================================
    # AUDITLOGS CONTROLLER COMPATIBILITY ROUTES
    # Single endpoint from Swagger: https://recycle.metadatads.com/swagger/index.html#/AuditLogs
    # GET /api/audit-logs
    # Organized in separate auditlogs/ folder
    # ============================================================================
    path('audit-logs/', include('zistino_apps.compatibility.auditlogs.urls')),
    
    # ============================================================================
    # BASKETS CONTROLLER COMPATIBILITY ROUTES
    # All 8 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Baskets
    # Organized in separate baskets/ folder
    # ============================================================================
    path('baskets/', include('zistino_apps.compatibility.baskets.urls')),
    
    # ============================================================================
    # BLOGCATEGORIES CONTROLLER COMPATIBILITY ROUTES
    # All 9 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/BlogCategories
    # Organized in separate blogcategories/ folder
    # ============================================================================
    path('blogcategories/', include('zistino_apps.compatibility.blogcategories.urls')),
    
    # ============================================================================
    # BLOGTAGS CONTROLLER COMPATIBILITY ROUTES
    # All 9 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/BlogTags
    # Organized in separate blogtags/ folder
    # ============================================================================
    path('blogtags/', include('zistino_apps.compatibility.blogtags.urls')),
    
    # ============================================================================
    # BLOGPOSTS CONTROLLER COMPATIBILITY ROUTES
    # All endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/BlogPosts
    # Organized in separate blogposts/ folder
    # ============================================================================
    path('blogposts/', include('zistino_apps.compatibility.blogposts.urls')),
    
    # ============================================================================
    # BOOKMARKS CONTROLLER COMPATIBILITY ROUTES
    # All 8 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Bookmarks
    # Organized in separate bookmarks/ folder
    # ============================================================================
    path('bookmarks/', include('zistino_apps.compatibility.bookmarks.urls')),
    
    # ============================================================================
    # BRANDS CONTROLLER COMPATIBILITY ROUTES
    # All 12 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Brands
    # Organized in separate brands/ folder
    # ============================================================================
    path('brands/', include('zistino_apps.compatibility.brands.urls')),
    
    # ============================================================================
    # CATEGORIES CONTROLLER COMPATIBILITY ROUTES
    # All 13 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Categories
    # Organized in separate categories/ folder
    # ============================================================================
    path('categories/', include('zistino_apps.compatibility.categories.urls')),
    
    # ============================================================================
    # CMS CONTROLLER COMPATIBILITY ROUTES
    # All 10 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Cms
    # Organized in separate cms/ folder
    # Note: by-page, by-group-name (query), and page-view already exist in main urls.py
    # ============================================================================
    path('cms/', include('zistino_apps.compatibility.cms.urls')),
    
    # ============================================================================
    # COLORS CONTROLLER COMPATIBILITY ROUTES
    # All 7 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Colors
    # Organized in separate colors/ folder
    # ============================================================================
    path('colors/', include('zistino_apps.compatibility.colors.urls')),
    
    # ============================================================================
    # COMMENTS CONTROLLER COMPATIBILITY ROUTES
    # All 16 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Comments
    # Organized in separate comments/ folder
    # ============================================================================
    path('comments/', include('zistino_apps.compatibility.comments.urls')),
    
    # ============================================================================
    # CONFIGURATIONS CONTROLLER COMPATIBILITY ROUTES
    # All 7 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Configurations
    # Organized in separate configurations/ folder
    # ============================================================================
    path('configurations/', include('zistino_apps.compatibility.configurations.urls')),
    
    # ============================================================================
    # COUPONS CONTROLLER COMPATIBILITY ROUTES
    # All 8 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Coupons
    # Organized in separate coupons/ folder
    # ============================================================================
    path('coupons/', include('zistino_apps.compatibility.coupons.urls')),
    
    # ============================================================================
    # COUPONUSES CONTROLLER COMPATIBILITY ROUTES
    # All 5 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/CouponUses
    # Organized in separate couponuses/ folder
    # Note: CouponUses are represented by BasketDiscount model
    # ============================================================================
    path('couponuses/', include('zistino_apps.compatibility.couponuses.urls')),
    
    # ============================================================================
    # FAQS CONTROLLER COMPATIBILITY ROUTES
    # All 10 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Faqs
    # Organized in separate faqs/ folder
    # ============================================================================
    path('faqs/', include('zistino_apps.compatibility.faqs.urls')),
    
    # ============================================================================
    # FILEMANAGER CONTROLLER COMPATIBILITY ROUTES
    # All 6 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/FileManager
    # Organized in separate filemanager/ folder
    # Note: File management functionality needs to be implemented
    # ============================================================================
    path('filemanager/', include('zistino_apps.compatibility.filemanager.urls')),
    
    # ============================================================================
    # FILEUPLOADER CONTROLLER COMPATIBILITY ROUTES
    # All 5 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/FileUploader
    # Organized in separate fileuploader/ folder
    # Note: File upload functionality needs to be implemented
    # ============================================================================
    path('fileuploader/', include('zistino_apps.compatibility.fileuploader.urls')),
    
    # ============================================================================
    # IDENTITY CONTROLLER COMPATIBILITY ROUTES
    # All 23 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Identity
    # Organized in separate identity/ folder
    # Note: Some endpoints map to existing authentication views
    # ============================================================================
    path('identity/', include('zistino_apps.compatibility.identity.urls')),
    
    # ============================================================================
    # LIKES CONTROLLER COMPATIBILITY ROUTES
    # All 4 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Likes
    # Organized in separate likes/ folder
    # Note: Like model needs to be created (migration required)
    # ============================================================================
    path('likes/', include('zistino_apps.compatibility.likes.urls')),
    
    # ============================================================================
    # LOCALIZATIONS CONTROLLER COMPATIBILITY ROUTES
    # All 8 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Localizations
    # Organized in separate localizations/ folder
    # Note: Localization model needs to be created (migration required)
    # ============================================================================
    path('localizations/', include('zistino_apps.compatibility.localizations.urls')),
    
    # ============================================================================
    # MAILTEMPLATES CONTROLLER COMPATIBILITY ROUTES
    # All 7 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/MailTemplates
    # Organized in separate mailtemplates/ folder
    # Note: MailTemplate model needs to be created (migration required)
    # ============================================================================
    path('mailtemplates/', include('zistino_apps.compatibility.mailtemplates.urls')),
    
    # ============================================================================
    # MAPZONE CONTROLLER COMPATIBILITY ROUTES
    # All 9 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/MapZone
    # Organized in separate mapzone/ folder
    # Note: Wraps existing Zone and UserZone views from users app
    # ============================================================================
    path('mapzone/', include('zistino_apps.compatibility.mapzone.urls')),
    
    # ============================================================================
    # ORDERS CONTROLLER COMPATIBILITY ROUTES
    # All 26 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Orders
    # Organized in separate orders/ folder
    # Note: Wraps existing Order views from orders app and adds missing functionality
    # ============================================================================
    path('orders/', include('zistino_apps.compatibility.orders.urls')),
    
    # ============================================================================
    # PAYMENTS CONTROLLER COMPATIBILITY ROUTES
    # All 16 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Payments
    # Organized in separate payments/ folder
    # Note: Most payment gateway endpoints (Stripe, PayPal) are placeholders and need actual integration
    # ============================================================================
    path('payments/', include('zistino_apps.compatibility.payments.urls')),
    
    # ============================================================================
    # PERSONAL CONTROLLER COMPATIBILITY ROUTES
    # All 23 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Personal
    # Organized in separate personal/ folder
    # Note: Some endpoints (blue badge, repair requests) are placeholders and need implementation
    # ============================================================================
    path('personal/', include('zistino_apps.compatibility.personal.urls')),
    
    # ============================================================================
    # POPULARPRODUCTS CONTROLLER COMPATIBILITY ROUTES
    # Note: This controller doesn't exist in the old Swagger, but Flutter app expects it.
    # We'll create basic endpoints similar to Products but for popular products.
    # Popularity is determined by order count (most ordered = most popular).
    # ============================================================================
    path('popularproducts/', include('zistino_apps.compatibility.popularproducts.urls')),

    # ============================================================================
    # PROBLEMS CONTROLLER COMPATIBILITY ROUTES
    # All 10 endpoints from Swagger
    # Organized in separate problems/ folder
    # Note: Wraps existing Problem views from products app
    # ============================================================================
    path('problems/', include('zistino_apps.compatibility.problems.urls')),

    # ============================================================================
    # PRODUCTPROBLEMS CONTROLLER COMPATIBILITY ROUTES
    # All 11 endpoints from Swagger
    # Organized in separate productproblems/ folder
    # Note: Wraps existing Problem views from products app, adds group functionality
    # ============================================================================
    path('productproblems/', include('zistino_apps.compatibility.productproblems.urls')),

    # ============================================================================
    # PRODUCTS CONTROLLER COMPATIBILITY ROUTES
    # All ~34 endpoints from Swagger (3 images)
    # Organized in separate products/ folder
    # Note: Wraps existing Product views from products app and adds client/admin endpoints
    # ============================================================================
    path('products/', include('zistino_apps.compatibility.products.urls')),

    # ============================================================================
    # PRODUCTSECTIONS CONTROLLER COMPATIBILITY ROUTES
    # All 10 endpoints from Swagger
    # Organized in separate productsections/ folder
    # Note: Wraps existing ProductSection views from products app
    # ============================================================================
    path('productsections/', include('zistino_apps.compatibility.productsections.urls')),

    # ============================================================================
    # PRODUCTSPECIFICATIONS CONTROLLER COMPATIBILITY ROUTES
    # All 7 endpoints from Swagger
    # Organized in separate productspecifications/ folder
    # Note: Wraps existing Specification views from products app
    # ============================================================================
    path('productspecifications/', include('zistino_apps.compatibility.productspecifications.urls')),

    # ============================================================================
    # REPAIRREQUESTARCHIVES CONTROLLER COMPATIBILITY ROUTES
    # All 5 endpoints from Swagger
    # Organized in separate repairrequestarchives/ folder
    # Note: Placeholder endpoints - RepairRequestArchive model needs to be created
    # ============================================================================
    path('repairrequestarchives/', include('zistino_apps.compatibility.repairrequestarchives.urls')),

    # ============================================================================
    # REPAIRREQUESTS CONTROLLER COMPATIBILITY ROUTES
    # All 13 endpoints from Swagger
    # Organized in separate repairrequests/ folder
    # Note: Placeholder endpoints - RepairRequest model needs to be created
    # ============================================================================
    path('repairrequests/', include('zistino_apps.compatibility.repairrequests.urls')),

    # ============================================================================
    # ROLECLAIMS CONTROLLER COMPATIBILITY ROUTES
    # All 7 endpoints from Swagger
    # Organized in separate roleclaims/ folder
    # Note: Placeholder endpoints - RoleClaim model needs to be created
    # ============================================================================
    path('roleclaims/', include('zistino_apps.compatibility.roleclaims.urls')),

    # ============================================================================
    # ROLES CONTROLLER COMPATIBILITY ROUTES
    # All 10 endpoints from Swagger
    # Organized in separate roles/ folder
    # Note: Placeholder endpoints - Role model needs to be created
    # ============================================================================
    path('roles/', include('zistino_apps.compatibility.roles.urls')),

    # ============================================================================
    # STATS CONTROLLER COMPATIBILITY ROUTES
    # All 2 endpoints from Swagger
    # Organized in separate stats/ folder
    # Note: Aggregates statistics from multiple models (orders, users, products, etc.)
    # ============================================================================
    path('stats/', include('zistino_apps.compatibility.stats.urls')),

    # ============================================================================
    # TAGS CONTROLLER COMPATIBILITY ROUTES
    # All 8 endpoints from Swagger
    # Organized in separate tags/ folder
    # Note: Wraps existing Tag views from content app
    # ============================================================================
    path('tags/', include('zistino_apps.compatibility.tags.urls')),

    # ============================================================================
    # TENANTS CONTROLLER COMPATIBILITY ROUTES
    # All 6 endpoints from Swagger
    # Organized in separate tenants/ folder
    # Note: Placeholder endpoints - Tenant model needs to be created
    # ============================================================================
    path('tenants/', include('zistino_apps.compatibility.tenants.urls')),

    # ============================================================================
    # TESTIMONIALS CONTROLLER COMPATIBILITY ROUTES
    # All 7 endpoints from Swagger
    # Organized in separate testimonials/ folder
    # Note: Wraps existing Testimonial views from content app
    # ============================================================================
    path('testimonials/', include('zistino_apps.compatibility.testimonials.urls')),

    # ============================================================================
    # TICKETS CONTROLLER COMPATIBILITY ROUTES
    # All 14 endpoints from Swagger
    # Organized in separate tickets/ folder
    # Note: Placeholder endpoints - Ticket and TicketMessage models need to be created
    # ============================================================================
    path('tickets/', include('zistino_apps.compatibility.tickets.urls')),

    # ============================================================================
    # TOKENS CONTROLLER COMPATIBILITY ROUTES
    # All 7 endpoints from Swagger
    # Organized in separate tokens/ folder
    # Note: Uses existing DRF Token model and authentication system
    # ============================================================================
    path('tokens/', include('zistino_apps.compatibility.tokens.urls')),

    # ============================================================================
    # USERS CONTROLLER COMPATIBILITY ROUTES
    # All 12 endpoints from Swagger
    # Organized in separate users/ folder
    # Note: Wraps existing User views from users app
    # ============================================================================
    path('users/', include('zistino_apps.compatibility.users.urls')),

    # ============================================================================
    # WARRANTIES CONTROLLER COMPATIBILITY ROUTES
    # All 9 endpoints from Swagger
    # Organized in separate warranties/ folder
    # Note: Wraps existing Warranty views from products app
    # ============================================================================
    path('warranties/', include('zistino_apps.compatibility.warranties.urls')),

    # ============================================================================
    # CONTACTUSMESSAGES CONTROLLER COMPATIBILITY ROUTES
    # All 8 endpoints from Swagger
    # Organized in separate contactusmessages/ folder
    # Note: Placeholder endpoints - ContactUsMessage model needs to be created
    # ============================================================================
    path('contactusmessages/', include('zistino_apps.compatibility.contactusmessages.urls')),

    # ============================================================================
    # DRIVERDELIVERY CONTROLLER COMPATIBILITY ROUTES
    # All 5 endpoints from Swagger
    # Organized in separate driverdelivery/ folder
    # Note: Wraps existing Delivery views from deliveries app
    # ============================================================================
    path('driverdelivery/', include('zistino_apps.compatibility.driverdelivery.urls')),

    # ============================================================================
    # VEHICLE CONTROLLER COMPATIBILITY ROUTES
    # Flutter expects: /api/v1/vehicle/{endpoint}
    # Organized in separate vehicle/ folder
    # Endpoints: GET/POST /api/v1/vehicle, GET/PUT/DELETE /api/v1/vehicle/{id},
    #            POST /api/v1/vehicle/search, GET /api/v1/vehicle/job-id/{jobid}
    # ============================================================================
    path('vehicle/', include('zistino_apps.compatibility.vehicle.urls')),

    # ============================================================================
    # LOCATIONS CONTROLLER COMPATIBILITY ROUTES
    # Flutter expects: /api/v1/locations/{endpoint}
    # Organized in separate locations/ folder
    # Endpoints: GET/POST /api/v1/locations, GET/PUT/DELETE /api/v1/locations/{id},
    #            POST /api/v1/locations/search, GET /api/v1/locations/job-id/{jobid}
    # ============================================================================
    path('locations/', include('zistino_apps.compatibility.locations.urls')),

    # ============================================================================
    # TRIP CONTROLLER COMPATIBILITY ROUTES
    # Flutter expects: /api/v1/trip/{endpoint}
    # Organized in separate trip/ folder
    # Endpoints: GET/POST /api/v1/trip, GET/PUT/DELETE /api/v1/trip/{id},
    #            POST /api/v1/trip/search, GET /api/v1/trip/job-id/{jobid}
    # ============================================================================
    path('trip/', include('zistino_apps.compatibility.trip.urls')),

    # ============================================================================
    # TRANSACTIONWALLET CONTROLLER COMPATIBILITY ROUTES
    # All 10 endpoints from Swagger
    # Organized in separate transactionwallet/ folder
    # Note: Wraps existing Wallet and Transaction views from payments app
    # ============================================================================
    path('transactionwallet/', include('zistino_apps.compatibility.transactionwallet.urls')),

]

