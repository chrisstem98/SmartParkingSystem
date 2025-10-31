from django.http import JsonResponse
from django.views import View
from django.db.models import Q
from PIL import Image
import os

from django.conf import settings
from .models import ParkingDetection


class ParkingHeatmapView(View):
    """
    Builds a heatmap overlay based on YOLO detections stored in ParkingDetection.
    Converts normalized coordinates to pixel positions on a base image.
    """

    BASE_IMAGE_REL = "media/parking_layout.jpg"  # base background image for visualization

    def get(self, request, *args, **kwargs):
        # --- Optional filters ---
        cls_filter = request.GET.get("cls")  # 'occupied', 'empty', or None
        start = request.GET.get("start")
        end = request.GET.get("end")

        qs = ParkingDetection.objects.all()

        if cls_filter in ("occupied", "empty"):
            qs = qs.filter(cls_name=cls_filter)

        if start and end:
            qs = qs.filter(created_at__date__range=[start, end])

        # --- Load base image for pixel scaling ---
        base_path = os.path.join(settings.BASE_DIR, self.BASE_IMAGE_REL)
        if not os.path.exists(base_path):
            return JsonResponse(
                {"error": f"Base image not found at {self.BASE_IMAGE_REL}"},
                status=500,
            )

        with Image.open(base_path) as im:
            base_w, base_h = im.size

        # --- Convert normalized YOLO coordinates to pixel positions ---
        points = []
        for d in qs.iterator():
            x = int(d.cx_norm * base_w)
            y = int(d.cy_norm * base_h)

            # Weight value based on detection type and confidence
            if d.cls_name == "occupied":
                val = max(0.05, min(1.0, d.conf))
            else:
                val = max(0.01, min(0.3, 0.1 * d.conf))

            points.append({
                "x": x,
                "y": y,
                "value": round(val, 3)
            })

        # --- Response ---
        return JsonResponse({
            "base_image": f"/{self.BASE_IMAGE_REL}",
            "max_value": 1.0,
            "points": points[:5000]  # Limit to avoid large payloads
        }, status=200)
