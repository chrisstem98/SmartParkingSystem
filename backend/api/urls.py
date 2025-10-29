from django.urls import path
from .views import UploadImageView
from .views_snapshot import ParkingSnapshotListView 

urlpatterns = [
    path('upload-image/', UploadImageView.as_view(), name='upload-image'),
    path('snapshots/', ParkingSnapshotListView.as_view(), name='snapshots_list'),
]