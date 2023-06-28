from django.contrib import admin
from .models import Station, Driver, Farmer, Hill, Transportation, Ratte, Schedule, Manager, YearlyStationExport, YearlyDistancePrice, YearlyHillStationDistance, DailySchedule, YearlyGasCharge
# Register your models here.

admin.site.register(Station)
admin.site.register(Driver)
admin.site.register(Farmer)
admin.site.register(Hill)
#admin.site.register(DailySchedule)
admin.site.register(Transportation)
admin.site.register(Ratte)
admin.site.register(Schedule)
admin.site.register(Manager)
admin.site.register(YearlyStationExport)
admin.site.register(YearlyDistancePrice)
admin.site.register(YearlyHillStationDistance)
admin.site.register(YearlyGasCharge)