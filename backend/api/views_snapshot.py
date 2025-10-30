from django.http import JsonResponse
from django.views import View
from django.utils.dateparse import parse_date
from .models import ParkingSnapshot


class ParkingSnapshotListView(View):
    """Returns paginated and filtered parking detection results as JSON."""

    def get(self, request, *args, **kwargs):
        # --- Base Query ---
        snapshots = ParkingSnapshot.objects.all().order_by('-timestamp')

        # --- Optional Filters ---
        date_str = request.GET.get('date')
        if date_str:
            try:
                date_obj = parse_date(date_str)
                if date_obj:
                    snapshots = snapshots.filter(timestamp__date=date_obj)
            except Exception:
                pass

        search = request.GET.get('search')
        if search:
            snapshots = snapshots.filter(image_name__icontains=search)

        # --- Pagination ---
        try:
            limit = int(request.GET.get('limit', 10))
            offset = int(request.GET.get('offset', 0))
        except ValueError:
            limit, offset = 10, 0

        total = snapshots.count()
        snapshots = snapshots[offset:offset + limit]

        # --- Serialize results ---
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

        response = {
            "count": total,
            "limit": limit,
            "offset": offset,
            "results": data,
        }
        return JsonResponse(response, safe=False, status=200)
