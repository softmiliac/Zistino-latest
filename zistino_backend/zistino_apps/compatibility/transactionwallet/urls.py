"""
URL patterns for TransactionWallet compatibility layer.
Provides all 10 endpoints matching Flutter app expectations.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Custom endpoints (must come before detail routes to avoid conflicts)
    path('search', views.TransactionWalletViewSet.as_view({'post': 'search'}), name='transactionwallet-search'),
    path('search/client', views.TransactionWalletClientSearchView.as_view(), name='transactionwallet-search-client'),
    path('mytransactionwallettotal', views.TransactionWalletMyTotalView.as_view(), name='transactionwallet-my-total'),
    path('mytransactionwallethistory', views.TransactionWalletMyHistoryView.as_view(), name='transactionwallet-my-history'),
    path('drivertransactionwallettotal', views.TransactionWalletDriverTotalView.as_view(), name='transactionwallet-driver-total'),
    path('drivertransactionwallettotalbyuserid', views.TransactionWalletDriverTotalByUserIdView.as_view(), name='transactionwallet-driver-total-by-userid'),
    
    # Custom routes for CRUD operations that accept both UUID and integer IDs (using <str:id> instead of <uuid:id>)
    path('<str:id>', views.TransactionWalletViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='transactionwallet-detail'),
    path('', views.TransactionWalletViewSet.as_view({'get': 'list', 'post': 'create'}), name='transactionwallet-list'),
]

