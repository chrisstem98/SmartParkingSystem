from django.http import JsonResponse
from django.views import View
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count
from .models import ParkingSnapshot, ParkingLot
from .services_stats import StatsService


class ParkingStatsView(View):
    """
    Returns parking statistics.
    Features:
    - All parking lots combined
    - Individual parking lot via ?site=UFPR01
    - Filters: ?date=, ?start=, ?end=, ?search=
    - Grouping: ?group_by=date
    """

    def get(self, request, *args, **kwargs):
        # Read query parameters
        site = request.GET.get("site")          
        date_str = request.GET.get("date")
        start_date = request.GET.get("start")
        end_date = request.GET.get("end")
        search = request.GET.get("search")
        group_by = request.GET.get("group_by")

        # Validate site if provided
        if site:
            if not ParkingLot.objects.filter(code=site).exists():
                return JsonResponse(
                    {"error": f"Parking lot '{site}' not found"}, status=404
                )

        # Use service to fetch snapshots based on filters
        snapshots = StatsService.filter_snapshots(
            site=site,
            date_str=date_str,
            start_date=start_date,
            end_date=end_date,
            search=search,
        )

        # If no data found
        if not snapshots.exists():
            return JsonResponse(
                {
                    "filters": {
                        "site": site,
                        "date": date_str,
                        "start": start_date,
                        "end": end_date,
                        "search": search,
                        "group_by": group_by,
                    },
                    "message": "No data found for the given filters.",
                    "results": [],
                },
                status=200,
            )

        # If grouping by date, return daily grouped results
        if group_by == "date":
            results = StatsService.group_by_date(snapshots)
            return JsonResponse(
                {
                    "filters": {
                        "site": site,
                        "date": date_str,
                        "start": start_date,
                        "end": end_date,
                        "search": search,
                        "group_by": group_by,
                    },
                    "results": results,
                },
                status=200,
            )

        # Aggregated summary for non-grouped mode
        aggregated = StatsService.aggregated(snapshots)

        total_empty = aggregated["total_empty"]
        total_occupied = aggregated["total_occupied"]
        total_snapshots = aggregated["total_snapshots"]
        occupancy_rate = aggregated["occupancy_rate"]
        latest = aggregated["latest"]

        # Build final response
        data = {
            "filters": {
                "site": site,
                "date": date_str,
                "start": start_date,
                "end": end_date,
                "search": search,
                "group_by": group_by,
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
            },
        }

        return JsonResponse(data, status=200)
