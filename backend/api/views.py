import os
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import ParkingLot, ParkingSnapshot, ParkingDetection
from .yolo_service_detector import YoloServiceDetector

@method_decorator(csrf_exempt, name='dispatch')
class UploadImageView(View):

    def post(self, request, *args, **kwargs):

        try:
            # 1) Validate site code
            site = request.GET.get("site")
            if not site:
                return JsonResponse({"error": "Missing ?site=UFPR04"}, status=400)

            try:
                lot = ParkingLot.objects.get(code=site)
            except ParkingLot.DoesNotExist:
                return JsonResponse({"error": f"Unknown site: {site}"}, status=404)

            # 2) Validate image
            if "image" not in request.FILES:
                return JsonResponse({"error": "No image provided"}, status=400)

            image_file = request.FILES["image"]

            # Save temp
            temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
            os.makedirs(temp_dir, exist_ok=True)

            temp_path = os.path.join(temp_dir, image_file.name)
            with open(temp_path, "wb+") as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

            # 3) YOLO inference
            model_path = os.path.join(settings.BASE_DIR, "models/best.pt")
            yolo = YoloServiceDetector(model_path)

            result = yolo.analyze_image(temp_path)
            counts = result["counts"]
            detections = result["detections"]
            annotated_path = result["annotated_path"]

            # 4) Move annotated image to MEDIA/results/<lot>/
            lot_results_dir = os.path.join(settings.MEDIA_ROOT, "results", lot.code)
            os.makedirs(lot_results_dir, exist_ok=True)

            final_annotated = os.path.join(lot_results_dir, image_file.name)

            os.replace(annotated_path, final_annotated)

            annotated_url = request.build_absolute_uri(
                f"{settings.MEDIA_URL}results/{lot.code}/{image_file.name}"
            )

            # 5) Save Snapshot
            snapshot = ParkingSnapshot.objects.create(
                lot=lot,
                image_name=image_file.name,
                empty_count=counts["empty"],
                occupied_count=counts["occupied"],
                annotated_image=image_file.name
            )

            # 6) Save detections one-by-one
            for d in detections:
                ParkingDetection.objects.create(
                    lot=lot,
                    snapshot=snapshot,
                    cls_name=d["cls_name"],
                    confidence=d["confidence"],
                    x=d["x"],
                    y=d["y"],
                    w=d["w"],
                    h=d["h"]
                )

            # 7) Cleanup temp
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return JsonResponse({
                "status": "ok",
                "site": lot.code,
                "snapshot_id": snapshot.id,
                "counts": counts,
                "annotated_url": annotated_url,
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
# End of backend/api/views.py