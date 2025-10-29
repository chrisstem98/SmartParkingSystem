from django.http import JsonResponse
from django.views import View
from .models import ParkingSnapshot


class ParkingSnapshotListView(View):
    """Returns all parking detection results as JSON."""

    def get(self, request, *args, **kwargs):
        # Get all snapshots ordered by most recent first
        snapshots = ParkingSnapshot.objects.all().order_by('-timestamp')

        # Serialize data into a simple JSON-friendly structure
        data = [
            {
                "id": s.id,
                "image_name": s.image_name,
                "timestamp": s.timestamp,
                "empty_count": s.empty_count,
                "occupied_count": s.occupied_count,
            }
            for s in snapshots
        ]

        return JsonResponse(data, safe=False, status=200)
