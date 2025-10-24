from django.http import JsonResponse
from django.views import View

class UploadImageView(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse({"message": "API working correctly!"})
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "GET method test OK"})