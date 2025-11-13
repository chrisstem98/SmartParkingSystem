# backend/api/models.py
from django.db import models

class ParkingLot(models.Model):
    """
    Represents a physical parking site (e.g., UFPR04, UFPR05, PUCPR).
    We keep a short 'code' for API queries and an optional base image
    to draw heatmaps on top of.
    """
    code = models.CharField(max_length=50, unique=True)  # short ID used in URLs, e.g., "UFPR04"
    name = models.CharField(max_length=120)              # human readable name
    base_image = models.ImageField(                      # optional background image for heatmap overlay
        upload_to='layouts/', blank=True, null=True
    )

    def __str__(self):
        return self.code


class ParkingSnapshot(models.Model):
    """
    One upload/inference event: the annotated result plus global counts.
    It belongs to a specific ParkingLot.
    """
    lot = models.ForeignKey(                             # link snapshot to a parking site
        ParkingLot, on_delete=models.CASCADE, related_name='snapshots'
    )
    image_name = models.CharField(max_length=255)        # original uploaded filename
    timestamp = models.DateTimeField(auto_now_add=True)  # when it was created
    empty_count = models.IntegerField(default=0)         # how many 'empty' detections
    occupied_count = models.IntegerField(default=0)      # how many 'occupied' detections
    annotated_image = models.CharField(                  # stored filename for annotated JPG (not full path)
        max_length=255, blank=True, null=True
    )

    def __str__(self):
        return f"{self.lot.code} | {self.image_name} @ {self.timestamp:%Y-%m-%d %H:%M:%S}"


class ParkingDetection(models.Model):
    """
    One bounding box detection that belongs to a snapshot (and thus to a lot).
    We store class, confidence and pixel bbox; (x, y) can be box center or top-left
    as long as we are consistent on read/write.
    """
    lot = models.ForeignKey(                             # denormalized link to lot for fast filtering
        ParkingLot, on_delete=models.CASCADE, related_name='detections'
    )
    snapshot = models.ForeignKey(                        # each detection belongs to a snapshot
        ParkingSnapshot, on_delete=models.CASCADE, related_name='detections'
    )
    cls_name = models.CharField(max_length=32)                # "empty" or "occupied"
    confidence = models.FloatField(default=1.0)
    x = models.IntegerField()                            # pixel x (we’ll use box center)
    y = models.IntegerField()                            # pixel y (we’ll use box center)
    w = models.IntegerField()                            # pixel width of bbox
    h = models.IntegerField()                            # pixel height of bbox

    def __str__(self):
        return f"{self.lot.code} | {self.cls_name} @{self.x},{self.y} conf={self.confidence:.2f}"
# End of backend/api/models.py