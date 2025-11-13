# api/admin.py
from django.contrib import admin
from .models import ParkingLot, ParkingSnapshot, ParkingDetection

@admin.register(ParkingLot)
class ParkingLotAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")

@admin.register(ParkingSnapshot)
class ParkingSnapshotAdmin(admin.ModelAdmin):
    list_display = ("lot", "image_name", "timestamp", "empty_count", "occupied_count")
    list_filter = ("lot", "timestamp")
    search_fields = ("image_name",)

@admin.register(ParkingDetection)
class ParkingDetectionAdmin(admin.ModelAdmin):
    list_display = ("lot", "snapshot", "cls_name", "confidence", "x", "y", "w", "h")
    list_filter = ("lot", "cls_name")
    search_fields = ("snapshot__image_name",)
# End of backend/api/admin.py   