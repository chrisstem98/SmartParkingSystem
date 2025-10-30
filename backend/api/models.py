from django.db import models

class ParkingSnapshot(models.Model):
    """Stores YOLO detection results for each processed parking image."""

    image_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    empty_count = models.IntegerField(default=0)
    occupied_count = models.IntegerField(default=0)
    annotated_image = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.image_name} - Empty: {self.empty_count}, Occupied: {self.occupied_count}"
