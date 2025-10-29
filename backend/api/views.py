import os
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .yolo_service_detector import YoloServiceDetector as YoloService
from .models import ParkingSnapshot


@method_decorator(csrf_exempt, name='dispatch')  #Allow POST without CSRF token.Testing purpose only.
class UploadImageView(View):
    """API endpoint to receive image from Pi and run YOLO inference."""

    def post(self, request, *args, **kwargs):
        try:
            #Check if image file exists in request
            if 'image' not in request.FILES:
                return JsonResponse({"error": "No image provided"}, status=400)

            image_file = request.FILES['image']

            #Save uploaded image temporarily
            upload_dir = os.path.join(settings.BASE_DIR, "media/uploads")
            os.makedirs(upload_dir, exist_ok=True)

            image_path = os.path.join(upload_dir, image_file.name)
            with open(image_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            #Run YOLO inference
            yolo = YoloService("backend/models/best.pt")
            counts = yolo.analyze_image(image_path)

            #Save YOLO results to the database
            ParkingSnapshot.objects.create(
                image_name=image_file.name,
                empty_count=counts.get("empty", 0),
                occupied_count=counts.get("occupied", 0),
            )

            #Prepare response
            response_data = {
                "status": "ok",
                "filename": image_file.name,
                "empty": counts.get("empty", 0),
                "occupied": counts.get("occupied", 0),
            }

            return JsonResponse(response_data, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
