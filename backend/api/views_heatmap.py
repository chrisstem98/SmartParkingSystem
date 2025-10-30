from django.http import JsonResponse
from django.views import View
from .models import ParkingSnapshot


class ParkingHeatmapView(View):
    """
    Returns aggregated data useful for heatmap visualization.
    This version computes frequency of occupied vs empty detections over time.
    """

    def get(self, request, *args, **kwargs):
        snapshots = ParkingSnapshot.objects.all()
        total_snapshots = snapshots.count()

        if total_snapshots == 0:
            return JsonResponse({
                "total_snapshots": 0,
                "heatmap_data": []
            }, status=200)

        # Create aggregated metrics (no real coordinates)
        # Here we simply calculate the average occupancy rate per image name
        occupancy_dict = {}

        for s in snapshots:
            name = s.image_name
            rate = s.occupied_count / max((s.empty_count + s.occupied_count), 1)
            if name not in occupancy_dict:
                occupancy_dict[name] = []
            occupancy_dict[name].append(rate)

        heatmap_data = []
        for name, rates in occupancy_dict.items():
            avg_rate = round(sum(rates) / len(rates), 3)
            heatmap_data.append({
                "image_name": name,
                "avg_occupancy": avg_rate
            })

        # Sort by occupancy (most occupied first)
        heatmap_data.sort(key=lambda x: x["avg_occupancy"], reverse=True)

        return JsonResponse({
            "total_snapshots": total_snapshots,
            "heatmap_data": heatmap_data[:20]  # limit to top 20 entries
        }, status=200)
