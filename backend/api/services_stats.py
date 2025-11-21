from django.db.models import Sum, Count, QuerySet
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date

from .models import ParkingSnapshot


class StatsService:
    """
    Service layer for parking statistics.
    Contains all filtering, grouping and aggregation logic.
    This keeps the view clean and easy to maintain.
    """

    @staticmethod
    def filter_snapshots(
        site: str | None = None,
        date_str: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        search: str | None = None,
    ) -> QuerySet[ParkingSnapshot]:
        """
        Returns a filtered queryset based on optional filters:
        - site: filter by parking lot code
        - date: filter by specific date
        - start/end: filter by date range
        - search: filter snapshots based on image filename
        """
        qs = ParkingSnapshot.objects.all()

        # Filter by parking lot code
        if site:
            qs = qs.filter(lot__code=site)

        # Filter by single date
        if date_str:
            d = parse_date(date_str)
            if d:
                qs = qs.filter(timestamp__date=d)

        # Filter by date range
        if start_date and end_date:
            s = parse_date(start_date)
            e = parse_date(end_date)
            if s and e:
                qs = qs.filter(timestamp__date__range=[s, e])

        # Text search in filename
        if search:
            qs = qs.filter(image_name__icontains=search)

        return qs

    @staticmethod
    def group_by_date(qs: QuerySet[ParkingSnapshot]) -> list[dict]:
        """
        Groups snapshots by date.
        This returns a daily aggregated view with:
        - total snapshots
        - total empty detections
        - total occupied detections
        - occupancy percentage
        """
        grouped = (
            qs.annotate(day=TruncDate("timestamp"))
            .values("day")
            .annotate(
                total_empty=Sum("empty_count"),
                total_occupied=Sum("occupied_count"),
                total_snapshots=Count("id"),
            )
            .order_by("day")
        )

        results: list[dict] = []
        for item in grouped:
            total = (item["total_empty"] or 0) + (item["total_occupied"] or 0)
            occupancy_rate = (
                round((item["total_occupied"] / total) * 100, 2)
                if total > 0
                else 0.0
            )

            results.append(
                {
                    "date": item["day"],
                    "total_snapshots": item["total_snapshots"],
                    "total_empty": item["total_empty"],
                    "total_occupied": item["total_occupied"],
                    "occupancy_rate": occupancy_rate,
                }
            )

        return results

    @staticmethod
    def aggregated(qs: QuerySet[ParkingSnapshot]) -> dict:
        """
        Returns non-grouped aggregated statistics:
        - total empty
        - total occupied
        - total snapshots
        - occupancy percentage
        - latest snapshot info
        """
        total_empty = qs.aggregate(Sum("empty_count"))["empty_count__sum"] or 0
        total_occupied = qs.aggregate(Sum("occupied_count"))["occupied_count__sum"] or 0
        total_snapshots = qs.count()

        occupancy_rate = (
            round((total_occupied / (total_occupied + total_empty)) * 100, 2)
            if (total_empty + total_occupied) > 0
            else 0.0
        )

        latest = qs.order_by("-timestamp").first()

        return {
            "total_empty": total_empty,
            "total_occupied": total_occupied,
            "total_snapshots": total_snapshots,
            "occupancy_rate": occupancy_rate,
            "latest": latest,
        }
# End of backend/api/services_stats.py