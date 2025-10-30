from django.http import JsonResponse
from django.views import View
from .models import ParkingSnapshot


class ParkingStatsView(View):
    """Returns aggregated parking statistics."""

    def get(self, request, *args, **kwargs):
        # Get all snapshots
        snapshots = ParkingSnapshot.objects.all()

        # If no data yet
        if not snapshots.exists():
            return JsonResponse({
                "total_snapshots": 0,
                "total_empty": 0,
                "total_occupied": 0,
                "latest_snapshot": None
            }, status=200)

        # Aggregate totals
        total_empty = sum(s.empty_count for s in snapshots)
        total_occupied = sum(s.occupied_count for s in snapshots)
        total_snapshots = snapshots.count()

        # Get most recent snapshot
        latest = snapshots.order_by('-timestamp').first()

        data = {
            "total_snapshots": total_snapshots,
            "total_empty": total_empty,
            "total_occupied": total_occupied,
            "latest_snapshot": {
                "image_name": latest.image_name,
                "timestamp": latest.timestamp,
                "empty": latest.empty_count,
                "occupied": latest.occupied_count,
            }
        }

        return JsonResponse(data, status=200)
