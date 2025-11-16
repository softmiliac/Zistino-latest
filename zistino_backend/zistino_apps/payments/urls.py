from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'transactions', views.TransactionViewSet)
router.register(r'wallets', views.WalletViewSet)
router.register(r'coupons', views.CouponViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('transactionwallet/mytransactionwallettotal', views.WalletViewSet.as_view({'get': 'my_total'})),
    path('transactionwallet/mytransactionwallethistory', views.TransactionViewSet.as_view({'get': 'my_history'})),
    path('transactionwallet/my-report', views.TransactionViewSet.as_view({'get': 'my_report'}), name='transactionwallet-my-report'),
    path('coupons/applycoupononbasket', views.CouponViewSet.as_view({'post': 'apply_on_basket'})),
    # Deposit Request endpoints
    path('deposits/request', views.CustomerDepositRequestViewSet.as_view({'post': 'create'}), name='deposit-request-create'),
    path('deposits/my-requests', views.CustomerDepositRequestViewSet.as_view({'get': 'list'}), name='deposit-request-list'),
    path('deposits/my-requests/<uuid:pk>', views.CustomerDepositRequestViewSet.as_view({'get': 'retrieve'}), name='deposit-request-detail'),
    path('deposits/search', views.AdminDepositRequestSearchView.as_view(), name='deposit-request-search'),
    path('deposits/<uuid:pk>/approve', views.AdminDepositRequestViewSet.as_view({'post': 'approve'}), name='deposit-request-approve'),
    path('deposits/<uuid:pk>/reject', views.AdminDepositRequestViewSet.as_view({'post': 'reject'}), name='deposit-request-reject'),
    # SMS Test endpoint
    path('test-sms', views.TestSMSView.as_view(), name='test-sms'),
    # SMS Pattern endpoint
    path('add-sms-pattern', views.AddSMSPatternView.as_view(), name='add-sms-pattern'),
    # SMS Pattern Test endpoint
    path('test-sms-pattern', views.TestSMSPatternView.as_view(), name='test-sms-pattern'),
    # Manager credit reports
    path('manager/customer-credits', views.ManagerCustomerCreditsView.as_view(), name='manager-customer-credits'),
    path('manager/driver-credits', views.ManagerDriverCreditsView.as_view(), name='manager-driver-credits'),
    # Manager manual payment record
    path('manager/payments/record', views.ManagerPaymentRecordView.as_view(), name='manager-payments-record'),
]
