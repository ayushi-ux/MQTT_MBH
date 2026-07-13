from django.contrib import admin
from .models import WaterReading, Device

admin.site.register(Device)
admin.site.register(WaterReading)
