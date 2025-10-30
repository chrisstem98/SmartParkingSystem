from django.http import JsonResponse
from django.views import View
from .models import ParkingSnapshot


class ParkingLiveView(View):
    """Returns the latest YOLO detection result for real-time dashboard."""

    def get(self, request, *args, **kwargs):
        # Get the most recent snapshot
        latest = ParkingSnapshot.objects.order_by('-timestamp').first()

        if not latest:
            return JsonResponse({
                "latest_snapshot": None,
                "message": "No detection data available yet."
            }, status=200)

        data = {
            "latest_snapshot": {
                "image_name": latest.image_name,
                "timestamp": latest.timestamp,
                "empty": latest.empty_count,
                "occupied": latest.occupied_count,
            }
        }

        return JsonResponse(data, status=200)
