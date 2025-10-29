from django.contrib import admin
from .models import ParkingSnapshot

@admin.register(ParkingSnapshot)
class ParkingSnapshotAdmin(admin.ModelAdmin):
    list_display = ("image_name", "timestamp", "empty_count", "occupied_count")
