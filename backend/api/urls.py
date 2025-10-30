from django.urls import path
from .views import UploadImageView
from .views_snapshot import ParkingSnapshotListView 
from .views_stats import ParkingStatsView
from .views_heatmap import ParkingHeatmapView
from .views_live import ParkingLiveView


urlpatterns = [
    path('upload-image/', UploadImageView.as_view(), name='upload-image'),
    path('snapshots/', ParkingSnapshotListView.as_view(), name='snapshots_list'),
    path('stats/', ParkingStatsView.as_view(), name='parking_stats'),
    path('heatmap/', ParkingHeatmapView.as_view(), name='parking_heatmap'),
    path('live/', ParkingLiveView.as_view(), name='parking_live'),
]