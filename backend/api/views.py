import os
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .yolo_service_detector import YoloServiceDetector as YoloService
from .models import ParkingSnapshot


@method_decorator(csrf_exempt, name='dispatch')  # Allow POST without CSRF token (for testing only)
class UploadImageView(View):
    """API endpoint to receive image from Pi simulator and run YOLO inference."""

    def post(self, request, *args, **kwargs):
        try:
            # 1. Validate image field
            if 'image' not in request.FILES:
                return JsonResponse({"error": "No image provided"}, status=400)

            image_file = request.FILES['image']

            # 2. Save uploaded image to MEDIA_ROOT/uploads
            upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
            os.makedirs(upload_dir, exist_ok=True)

            image_path = os.path.join(upload_dir, image_file.name)
            with open(image_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # 3. Run YOLO inference
            model_path = os.path.join(settings.BASE_DIR, "models/best.pt")
            yolo = YoloService(model_path)
            
            result = yolo.analyze_image(image_path)
            counts = result["counts"]
            annotated_path = result["annotated_path"]

            # 4. Save detection results in DB
            ParkingSnapshot.objects.create(
                image_name=image_file.name,
                empty_count=counts.get("empty", 0),
                occupied_count=counts.get("occupied", 0),
                annotated_image=os.path.basename(annotated_path)
            )

            # 5. Send response back to client
            response_data = {
                "status": "ok",
                "filename": image_file.name,
                "empty": counts.get("empty", 0),
                "occupied": counts.get("occupied", 0),
            }

            return JsonResponse(response_data, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
