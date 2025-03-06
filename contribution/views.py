# Create your views here.
from django.http import JsonResponse
from .models import Receipt

def get_new_receipt_number(request):
    new_receipt_number = Receipt.generate_receipt_number()
    return JsonResponse({"new_receipt_number": new_receipt_number})
