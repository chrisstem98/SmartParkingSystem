from django.db import models

class ParkingSnapshot(models.Model):
    image_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    empty_count = models.IntegerField(default=0)
    occupied_count = models.IntegerField(default=0)
    annotated_image = models.CharField(max_length=255, blank=True, null=True)
  

class ParkingDetection(models.Model):
    snapshot = models.ForeignKey(ParkingSnapshot, on_delete=models.CASCADE, related_name="detections")
    cls_name = models.CharField(max_length=32)        # 'empty' ή 'occupied'
    conf = models.FloatField(default=0.0)             # confidence 0..1
    cx_norm = models.FloatField()                     # center_x / img_w  (0..1)
    cy_norm = models.FloatField()                     # center_y / img_h  (0..1)
    w_norm = models.FloatField(null=True, blank=True) # optional: width/img_w
    h_norm = models.FloatField(null=True, blank=True) # optional: height/img_h
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["cls_name"]),
        ]
