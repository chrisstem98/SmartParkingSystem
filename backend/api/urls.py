from django.urls import path
from .views import UploadImageView
from .views_snapshot import ParkingSnapshotListView 
from .views_stats import ParkingStatsView
from .views_heatmap import ParkingHeatmapView
from .views_live import ParkingLiveView
from .views_lot import ParkingLotsView
from . import views_reservations


urlpatterns = [
    path('upload-image/', UploadImageView.as_view(), name='upload-image'),
    path('snapshots/', ParkingSnapshotListView.as_view(), name='snapshots_list'),
    path('stats/', ParkingStatsView.as_view(), name='parking_stats'),
    path('heatmap/', ParkingHeatmapView.as_view(), name='parking_heatmap'),
    path('live/', ParkingLiveView.as_view(), name='parking_live'),
    path("parking-lots/", ParkingLotsView.as_view(), name="parking-lots"),
    path("reservations/", views_reservations.create_reservation),
    path("reservations/list/", views_reservations.list_reservations),
    path("reservations/<int:reservation_id>/", views_reservations.cancel_reservation),


]