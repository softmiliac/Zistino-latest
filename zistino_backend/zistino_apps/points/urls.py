from django.urls import path, include
from zistino_apps.compatibility.router import NoTrailingSlashRouter
from . import views

router = NoTrailingSlashRouter()
# Admin lottery management (CRUD + actions)
router.register(r'lotteries', views.AdminLotteryViewSet, basename='admin-lottery')

urlpatterns = [
    # Customer endpoints - Points
    path('points/my-balance', views.CustomerPointsViewSet.as_view({'get': 'my_balance'}), name='points-my-balance'),
    path('points/my-history', views.CustomerPointsViewSet.as_view({'get': 'my_history'}), name='points-my-history'),
    
    # Customer endpoints - Referrals
    path('referrals/my-code', views.CustomerReferralViewSet.as_view({'get': 'my_code'}), name='referral-my-code'),
    path('referrals/my-referrals', views.CustomerReferralViewSet.as_view({'get': 'my_referrals'}), name='referral-my-referrals'),
    
    # Customer endpoints - Lottery (MUST come BEFORE router to avoid conflicts)
    path('lotteries/active', views.CustomerLotteryViewSet.as_view({'get': 'active'}), name='lottery-active'),
    path('lotteries/my-tickets', views.CustomerLotteryViewSet.as_view({'get': 'my_tickets'}), name='lottery-my-tickets'),
    path('lotteries/winners', views.CustomerLotteryViewSet.as_view({'get': 'winners'}), name='lottery-winners'),
    # Customer lottery detail and buy-tickets (specific paths that won't conflict with router)
    path('lotteries/<uuid:pk>/detail', views.CustomerLotteryViewSet.as_view({'get': 'retrieve'}), name='lottery-detail'),
    path('lotteries/<uuid:pk>/buy-tickets', views.CustomerLotteryViewSet.as_view({'post': 'buy_tickets'}), name='lottery-buy-tickets'),
    
    # Admin endpoints - Points management
    path('points/search', views.AdminPointTransactionSearchView.as_view(), name='admin-point-transactions-search'),
    path('points/manual-award', views.AdminManualAwardPointsView.as_view(), name='admin-points-manual-award'),
    
    # Admin endpoints - Referral management
    path('referrals/search', views.AdminReferralSearchView.as_view(), name='admin-referrals-search'),
    
    # Admin endpoints - Lottery search (MUST come BEFORE router to avoid conflicts)
    path('lotteries/search', views.AdminLotteryViewSet.as_view({'post': 'search'}), name='lottery-search'),
    
    # Router (admin lottery CRUD + actions) - MUST come LAST to avoid conflicts
    path('', include(router.urls)),
]

