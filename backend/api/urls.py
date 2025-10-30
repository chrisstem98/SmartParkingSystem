from django.urls import path
from .views import UploadImageView
from .views_snapshot import ParkingSnapshotListView 
from .views_stats import ParkingStatsView


urlpatterns = [
    path('upload-image/', UploadImageView.as_view(), name='upload-image'),
    path('snapshots/', ParkingSnapshotListView.as_view(), name='snapshots_list'),
    path('stats/', ParkingStatsView.as_view(), name='parking_stats'),
]