from django.http import JsonResponse
from django.views import View
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count
from .models import ParkingSnapshot


class ParkingStatsView(View):
    """Returns aggregated parking statistics with optional filters and daily grouping."""

    def get(self, request, *args, **kwargs):
        # Base queryset
        snapshots = ParkingSnapshot.objects.all()

        # Filters
        date_str = request.GET.get('date')
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        search = request.GET.get('search')
        group_by = request.GET.get('group_by')  # e.g., 'date'

        if date_str:
            date_obj = parse_date(date_str)
            if date_obj:
                snapshots = snapshots.filter(timestamp__date=date_obj)

        if start_date and end_date:
            start_obj = parse_date(start_date)
            end_obj = parse_date(end_date)
            if start_obj and end_obj:
                snapshots = snapshots.filter(timestamp__date__range=[start_obj, end_obj])

        if search:
            snapshots = snapshots.filter(image_name__icontains=search)

        # If no results
        if not snapshots.exists():
            return JsonResponse({
                "filters": {
                    "date": date_str,
                    "start": start_date,
                    "end": end_date,
                    "search": search,
                    "group_by": group_by
                },
                "message": "No data found for the given filters.",
                "results": []
            }, status=200)

        # --- GROUP BY DATE ---
        if group_by == 'date':
            from django.db.models.functions import TruncDate

            grouped = (
                snapshots
                .annotate(day=TruncDate('timestamp'))
                .values('day')
                .annotate(
                    total_empty=Sum('empty_count'),
                    total_occupied=Sum('occupied_count'),
                    total_snapshots=Count('id')
                )
                .order_by('day')
            )

            # Serialize results with occupancy rate
            results = []
            for item in grouped:
                total = item['total_empty'] + item['total_occupied']
                occupancy_rate = round(
                    (item['total_occupied'] / total) * 100, 2
                ) if total > 0 else 0.0

                results.append({
                    "date": item['day'],
                    "total_snapshots": item['total_snapshots'],
                    "total_empty": item['total_empty'],
                    "total_occupied": item['total_occupied'],
                    "occupancy_rate": occupancy_rate
                })

            return JsonResponse({
                "filters": {
                    "date": date_str,
                    "start": start_date,
                    "end": end_date,
                    "search": search,
                    "group_by": group_by
                },
                "results": results
            }, status=200)

        # --- AGGREGATED (NO GROUPING) ---
        total_empty = snapshots.aggregate(Sum('empty_count'))['empty_count__sum'] or 0
        total_occupied = snapshots.aggregate(Sum('occupied_count'))['occupied_count__sum'] or 0
        total_snapshots = snapshots.count()
        occupancy_rate = round(
            (total_occupied / (total_occupied + total_empty)) * 100, 2
        ) if (total_empty + total_occupied) > 0 else 0.0

        latest = snapshots.order_by('-timestamp').first()

        data = {
            "filters": {
                "date": date_str,
                "start": start_date,
                "end": end_date,
                "search": search,
                "group_by": group_by
            },
            "total_snapshots": total_snapshots,
            "total_empty": total_empty,
            "total_occupied": total_occupied,
            "occupancy_rate": occupancy_rate,
            "latest_snapshot": {
                "image_name": latest.image_name,
                "timestamp": latest.timestamp,
                "empty": latest.empty_count,
                "occupied": latest.occupied_count,
            }
        }

        return JsonResponse(data, status=200)
