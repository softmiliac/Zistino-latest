from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'verification-codes', views.VerificationCodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('send-code', views.SendCodeView.as_view(), name='send-code'),
    path('verify-code', views.VerifyCodeView.as_view(), name='verify-code'),
    path('login', views.LoginView.as_view(), name='login'),
    path('tokens/send-code', views.SendCodeView.as_view(), name='tokens-send-code'),
    path('tokens/token-by-code', views.LoginView.as_view(), name='tokens-login-by-code'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('forgot-password', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password', views.ResetPasswordView.as_view(), name='reset-password'),
]
