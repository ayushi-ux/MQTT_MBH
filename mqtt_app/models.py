from django.db import models


class Device(models.Model):
    mac_address = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    device_name = models.CharField(max_length=100, default="Water Tank")
    total_height = models.FloatField(default=3.0)
    total_volume = models.FloatField(default=1000.0)
    min_percentage = models.FloatField(default=20.0)
    max_percentage = models.FloatField(default=90.0)
    deep_sleep = models.IntegerField(default=0)
    sleep_interval = models.IntegerField(default=300)
    sensor_interval = models.IntegerField(default=5000)  # How often sensor reads (ms)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_name} ({self.mac_address})"


class WaterReading(models.Model):
    # Link reading to a device
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="readings", null=True, blank=True)

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

    # Diagnostics
    faults = models.IntegerField(default=0)  # System fault bitmask (0-255)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        device_name = self.device.device_name if self.device else "Unknown"
        return f"{device_name} | Water {self.percentage}% | Motor {self.motor_status} | {self.created_at}"

