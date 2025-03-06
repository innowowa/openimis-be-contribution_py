from django.urls import path
from . import views

urlpatterns = [
    path('get-new-receipt-number/', views.get_new_receipt_number, name='get-new-receipt-number'),
]
