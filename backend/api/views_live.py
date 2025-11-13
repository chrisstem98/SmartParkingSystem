# backend/api/views_live.py
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import ParkingSnapshot, ParkingLot


@method_decorator(csrf_exempt, name="dispatch")
class ParkingLiveView(View):
    """
    Returns the latest YOLO detection result for a specific parking lot.
    Frontend calls: /api/latest-snapshot/?site=UFPR04
    """

    def get(self, request, *args, **kwargs):
        # 1) Read site code from query ?site=...
        site = request.GET.get("site")
        if not site:
            return JsonResponse({"error": "Missing ?site=UFPR04"}, status=400)

        # 2) Ensure parking lot exists
        try:
            lot = ParkingLot.objects.get(code=site)
        except ParkingLot.DoesNotExist:
            return JsonResponse({"error": f"Unknown site: {site}"}, status=404)

        # 3) Find latest snapshot for this lot
        latest = (
            ParkingSnapshot.objects.filter(lot=lot)
            .order_by("-timestamp")
            .first()
        )

        if not latest:
            return JsonResponse(
                {
                    "site": lot.code,
                    "latest_snapshot": None,
                    "message": "No detection data available yet for this lot.",
                },
                status=200,
            )

        # 4) Build correct annotated image URL:
        #    /media/results/<LOT_CODE>/<filename>
        annotated_url = request.build_absolute_uri(
            f"{settings.MEDIA_URL}results/{lot.code}/{latest.annotated_image}"
        )

        # (Optional) if θέλεις και το original (μη annotated) image_url, μπορείς
        # να το προσθέσεις αργότερα.

        # 5) Return JSON payload used by LiveView.tsx
        data = {
            "site": lot.code,
            "latest_snapshot": {
                "timestamp": latest.timestamp,
                "empty": latest.empty_count,
                "occupied": latest.occupied_count,
                "annotated_url": annotated_url,
            },
        }

        return JsonResponse(data, status=200)
# End of backend/api/views_live.py