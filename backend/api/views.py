import os
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .yolo_service_detector import YoloServiceDetector as YoloService
from .models import ParkingSnapshot, ParkingDetection


@method_decorator(csrf_exempt, name="dispatch")
class UploadImageView(View):
    """
    API endpoint:
      - Receives image from Pi simulator
      - Runs YOLO inference
      - Saves annotated image (locally or to MinIO)
      - Stores detections and counts in the database
    """

    def post(self, request, *args, **kwargs):
        try:
            # 1️⃣ Validate uploaded image
            if "image" not in request.FILES:
                return JsonResponse({"error": "No image provided"}, status=400)

            image_file = request.FILES["image"]

            # 2️⃣ Save temporarily for YOLO inference
            temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, image_file.name)
            with open(temp_path, "wb+") as dest:
                for chunk in image_file.chunks():
                    dest.write(chunk)

            # 3️⃣ Run YOLO detection
            model_path = os.path.join(settings.BASE_DIR, "models/best.pt")
            yolo = YoloService(model_path)
            result = yolo.analyze_image(temp_path)

            counts = result["counts"]
            annotated_path = result["annotated_path"]
            detections = result.get("detections", [])

            # 4️⃣ Save annotated image
            if getattr(settings, "USE_S3", False):
                # Upload to MinIO/S3
                with open(annotated_path, "rb") as f:
                    file_name = os.path.basename(annotated_path)
                    default_storage.save(file_name, ContentFile(f.read()))

                annotated_url = (
                    f"{settings.MINIO_PUBLIC_ENDPOINT}/"
                    f"{settings.AWS_STORAGE_BUCKET_NAME}/{file_name}"
                )
            else:
                # Save locally under MEDIA_ROOT/results/
                results_dir = os.path.join(settings.MEDIA_ROOT, "results")
                os.makedirs(results_dir, exist_ok=True)

                file_name = os.path.basename(annotated_path)
                final_path = os.path.join(results_dir, file_name)

                os.replace(annotated_path, final_path)

                annotated_url = request.build_absolute_uri(
                    os.path.join(settings.MEDIA_URL, "results", file_name)
                )

            # 5️⃣ Create ParkingSnapshot entry
            snapshot = ParkingSnapshot.objects.create(
                image_name=image_file.name,
                empty_count=counts.get("empty", 0),
                occupied_count=counts.get("occupied", 0),
                annotated_image=file_name,
            )

            # 6️⃣ Save YOLO detections
            det_rows = []
            for d in detections:
                det_rows.append(
                    ParkingDetection(
                        snapshot=snapshot,
                        cls_name=d["cls_name"],
                        conf=d["conf"],
                        cx_norm=d["cx_norm"],
                        cy_norm=d["cy_norm"],
                        w_norm=d.get("w_norm"),
                        h_norm=d.get("h_norm"),
                    )
                )

            if det_rows:
                ParkingDetection.objects.bulk_create(det_rows)

            # 7️⃣ Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            # ✅ Response
            return JsonResponse(
                {
                    "status": "ok",
                    "filename": file_name,
                    "empty": counts.get("empty", 0),
                    "occupied": counts.get("occupied", 0),
                    "detections_saved": len(det_rows),
                    "annotated_url": annotated_url,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
