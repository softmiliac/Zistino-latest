"""
Payment models are imported from payments app.
This file is kept for compatibility but imports from payments app.
"""
from zistino_apps.payments.models import Wallet, Transaction, Coupon, BasketDiscount, DepositRequest

__all__ = ['Wallet', 'Transaction', 'Coupon', 'BasketDiscount', 'DepositRequest']

