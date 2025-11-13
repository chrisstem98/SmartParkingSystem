# backend/api/views_heatmap.py

from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from .models import ParkingLot, ParkingDetection


class ParkingHeatmapView(View):
    """
    Generates heatmap data for a specific parking lot.
    Heatmap points come from YOLO bounding box centers.
    """

    def get(self, request, *args, **kwargs):
        # --- 1) Read site parameter ---
        site_code = request.GET.get("site")
        if not site_code:
            return JsonResponse({"error": "Missing ?site= parameter"}, status=400)

        # --- 2) Resolve parking lot ---
        lot = get_object_or_404(ParkingLot, code=site_code)

        # --- 3) Base image URL for drawing heatmap ---
        background_url = None
        if lot.base_image:
            background_url = request.build_absolute_uri(lot.base_image.url)

        # --- 4) Fetch all detections for this parking lot ---
        detections = ParkingDetection.objects.filter(lot=lot)

        if not detections.exists():
            return JsonResponse({
                "site": site_code,
                "background_url": background_url,
                "heatmap_points": [],
                "message": "No detections stored for this parking lot yet."
            })

        # --- 5) Aggregate detections by pixel position ---
        clusters = {}  # key: (x,y), value: list of 0/1

        for d in detections:
            key = (d.x, d.y)

            # occupied → stronger heat
            occ_flag = 1 if d.cls_name == "occupied" else 0

            if key not in clusters:
                clusters[key] = []

            clusters[key].append(occ_flag)

        # --- 6) Convert clusters to final heatmap points ---
        heatmap_points = []
        for (x, y), values in clusters.items():
            avg_val = sum(values) / len(values)  # range 0..1

            heatmap_points.append({
                "x": x,
                "y": y,
                "value": round(avg_val, 3),
            })

        # --- 7) Final JSON ---
        return JsonResponse({
            "site": site_code,
            "background_url": background_url,
            "max_value": 1.0,
            "heatmap_points": heatmap_points
        })
# End of backend/api/views_heatmap.py