import os
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from urllib.parse import urljoin

from .yolo_service_detector import YoloServiceDetector as YoloService
from .models import ParkingSnapshot


@method_decorator(csrf_exempt, name='dispatch')
class UploadImageView(View):
    """
    API endpoint to receive image from Pi simulator,
    run YOLO inference, and save only the annotated result.
    """

    def post(self, request, *args, **kwargs):
        try:
            # Validate file field
            if 'image' not in request.FILES:
                return JsonResponse({"error": "No image provided"}, status=400)

            image_file = request.FILES['image']

            # Save temporarily for YOLO inference (not stored permanently)
            temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, image_file.name)

            with open(temp_path, "wb+") as dest:
                for chunk in image_file.chunks():
                    dest.write(chunk)

            # Run YOLO detection
            model_path = os.path.join(settings.BASE_DIR, "models/best.pt")
            yolo = YoloService(model_path)
            result = yolo.analyze_image(temp_path)

            counts = result["counts"]
            annotated_path = result["annotated_path"]

            # Save only the annotated image (either to MinIO or local)
            if getattr(settings, "USE_S3", False):
                # Upload annotated image to MinIO
                with open(annotated_path, "rb") as f:
                    file_name = os.path.basename(annotated_path)
                    default_storage.save(file_name, ContentFile(f.read()))

                annotated_url = f"{settings.MINIO_PUBLIC_ENDPOINT}/{settings.AWS_STORAGE_BUCKET_NAME}/{file_name}"
            else:
                # Save locally in MEDIA_ROOT/results/
                results_dir = os.path.join(settings.MEDIA_ROOT, "results")
                os.makedirs(results_dir, exist_ok=True)

                file_name = os.path.basename(annotated_path)
                final_path = os.path.join(results_dir, file_name)

                # Move annotated image to results/
                os.replace(annotated_path, final_path)

                annotated_url = request.build_absolute_uri(
                    os.path.join(settings.MEDIA_URL, "results", file_name)
                )

            # Store results in DB
            ParkingSnapshot.objects.create(
                image_name=image_file.name,
                empty_count=counts.get("empty", 0),
                occupied_count=counts.get("occupied", 0),
                annotated_image=file_name,
            )

            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            #Return response
            return JsonResponse(
                {
                    "status": "ok",
                    "filename": file_name,
                    "empty": counts.get("empty", 0),
                    "occupied": counts.get("occupied", 0),
                    "annotated_url": annotated_url,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
