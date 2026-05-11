from django.db import models


class WaterReading(models.Model):
    # Tank configuration
    total_height = models.FloatField()
    total_volume = models.FloatField()

    # Sensor data
    distance = models.FloatField()
    percentage = models.FloatField()
    filled_water_in_volume = models.FloatField()
    battery_voltage = models.FloatField()

    # Motor state
    motor_mode = models.IntegerField()     # 0 = auto, 1 = manual
    motor_status = models.IntegerField()   # 0 = off, 1 = on

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Water {self.percentage}% | Motor {self.motor_status} | {self.created_at}"
