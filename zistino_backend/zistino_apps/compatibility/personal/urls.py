"""
Personal compatibility URL routes for Flutter apps.
All 23 endpoints from Swagger: https://recycle.metadatads.com/swagger/index.html#/Personal

Flutter expects: /api/v1/personal/{endpoint}
All endpoints are tagged with 'Personal' to appear grouped in Swagger UI.

Endpoints:
1. GET /api/v1/personal/profile - Get profile
2. PUT /api/v1/personal/profile - Update profile
3. GET /api/v1/personal/profilewithcoins - Get profile with coins
4. GET /api/v1/personal/profilecached - Get profile (cached)
5. PUT /api/v1/personal/profileadmin - Update profile (Admin)
6. PUT /api/v1/personal/profileupdatewithadmin/{userId} - Update user profile (Admin)
7. GET /api/v1/personal/adminactiveuser/{userId} - Activate user (Admin)
8. GET /api/v1/personal/admindeactiveuser/{userId} - Deactivate user (Admin)
9. POST /api/v1/personal/representative - Update representative
10. POST /api/v1/personal/profiledatebyrepresentativedate - Get representatives by date
11. POST /api/v1/personal/setbluebadge - Set blue badge (Admin)
12. POST /api/v1/personal/requestbluebadge - Request blue badge
13. POST /api/v1/personal/requestrole - Request role
14. POST /api/v1/personal/reset-password - Reset password (Admin)
15. PUT /api/v1/personal/change-password - Change password
16. GET /api/v1/personal/permissions - Get permissions
17. POST /api/v1/personal/repairrequests - Get repair requests
18. GET /api/v1/personal/numberofrepairrequestsinstatus - Get repair request counts
19. GET /api/v1/personal/repairrequest/{id} - Get repair request
20. POST /api/v1/personal/repairrequestdocument - Add repair request document
21. POST /api/v1/personal/repairrequestmessage - Add repair request message
22. GET /api/v1/personal/repairrequestmessagesbyrepairid/{id} - Get repair request messages
23. GET /api/v1/personal/client/userinfo/{id} - Get user info
"""
from django.urls import path
from . import views

urlpatterns = [
    # PROFILE ENDPOINTS
    # Note: /profile endpoint handles both GET and PUT - we'll create a combined view
    path('profile', views.PersonalProfileCombinedView.as_view(), name='personal-profile'),
    path('profilewithcoins', views.PersonalProfileWithCoinsView.as_view(), name='personal-profilewithcoins'),
    path('profilecached', views.PersonalProfileCachedView.as_view(), name='personal-profilecached'),
    
    # ADMIN PROFILE ENDPOINTS
    path('profileadmin', views.PersonalProfileAdminView.as_view(), name='personal-profileadmin'),
    path('profileupdatewithadmin/<str:userId>', views.PersonalProfileUpdateWithAdminView.as_view(), name='personal-profileupdatewithadmin'),
    path('adminactiveuser/<str:userId>', views.PersonalAdminActiveUserView.as_view(), name='personal-adminactiveuser'),
    path('admindeactiveuser/<str:userId>', views.PersonalAdminDeactiveUserView.as_view(), name='personal-admindeactiveuser'),
    
    # REPRESENTATIVE ENDPOINTS
    path('representative', views.PersonalRepresentativeView.as_view(), name='personal-representative'),
    path('profiledatebyrepresentativedate', views.PersonalProfileDateByRepresentativeDateView.as_view(), name='personal-profiledatebyrepresentativedate'),
    
    # BLUE BADGE ENDPOINTS
    path('setbluebadge', views.PersonalSetBlueBadgeView.as_view(), name='personal-setbluebadge'),
    path('requestbluebadge', views.PersonalRequestBlueBadgeView.as_view(), name='personal-requestbluebadge'),
    
    # ROLE REQUEST ENDPOINTS
    path('requestrole', views.PersonalRequestRoleView.as_view(), name='personal-requestrole'),
    
    # PASSWORD ENDPOINTS
    path('reset-password', views.PersonalResetPasswordView.as_view(), name='personal-reset-password'),
    path('change-password', views.PersonalChangePasswordView.as_view(), name='personal-change-password'),
    
    # PERMISSIONS ENDPOINT
    path('permissions', views.PersonalPermissionsView.as_view(), name='personal-permissions'),
    
    # REPAIR REQUEST ENDPOINTS
    path('repairrequests', views.PersonalRepairRequestsView.as_view(), name='personal-repairrequests'),
    path('numberofrepairrequestsinstatus', views.PersonalNumberOfRepairRequestsInStatusView.as_view(), name='personal-numberofrepairrequestsinstatus'),
    path('repairrequest/<str:id>', views.PersonalRepairRequestView.as_view(), name='personal-repairrequest'),
    path('repairrequestdocument', views.PersonalRepairRequestDocumentView.as_view(), name='personal-repairrequestdocument'),
    path('repairrequestmessage', views.PersonalRepairRequestMessageView.as_view(), name='personal-repairrequestmessage'),
    path('repairrequestmessagesbyrepairid/<str:id>', views.PersonalRepairRequestMessagesByRepairIdView.as_view(), name='personal-repairrequestmessagesbyrepairid'),
    
    # CLIENT USER INFO
    path('client/userinfo/<str:id>', views.PersonalClientUserInfoView.as_view(), name='personal-client-userinfo'),
]

