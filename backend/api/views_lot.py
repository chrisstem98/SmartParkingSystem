from django.http import JsonResponse
from django.views import View
from .models import ParkingLot

class ParkingLotsView(View):
    """Return list of available parking lots."""

    def get(self, request, *args, **kwargs):
        lots = ParkingLot.objects.all()
        data = [{"code": lot.code, "name": lot.name} for lot in lots]
        return JsonResponse({"parking_lots": data}, status=200)
