import os
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt 
from .yolo_service_detector import YoloServiceDetector as YoloService


#@method_decorator(csrf_exempt, name='dispatch')For testing purposes, disable CSRF. 
class UploadImageView(View):
    """API endpoint to receive image from Pi and run YOLO inference."""

    def post(self, request, *args, **kwargs):
        try:
            if 'image' not in request.FILES:
                return JsonResponse({"error": "No image provided"}, status=400)

            image_file = request.FILES['image']

            upload_dir = os.path.join(settings.BASE_DIR, "media/uploads")
            os.makedirs(upload_dir, exist_ok=True)

            image_path = os.path.join(upload_dir, image_file.name)
            with open(image_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            yolo = YoloService("models/best.pt")
            counts = yolo.analyze_image(image_path)

            response_data = {
                "status": "ok",
                "filename": image_file.name,
                "empty": counts.get("empty", 0),
                "occupied": counts.get("occupied", 0),
            }

            return JsonResponse(response_data, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
