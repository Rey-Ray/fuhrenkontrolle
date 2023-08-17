from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Ratte(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(default="ratte", max_length=20)
    def __str__(self):
         return self.user.username


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(default='manager', max_length=20)
    def __str__(self):
         return self.user.username


class Driver(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=50, blank=True, null=True)
    container_size = models.FloatField(blank=True, null=True)
    #telephone = models.IntegerField()
    def __str__(self):
        return f'{self.name}'


class Farmer(models.Model):
    name = models.CharField(max_length=50)
    #telephone = models.IntegerField()
    def __str__(self):
        return f'{self.name}'


class Station(models.Model):
    station_name = models.CharField(max_length=50)
    def __str__(self):
        return self.station_name


class Hill(models.Model):
    size = models.CharField(max_length=50)
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    def __str__(self):
        name = f'{self.farmer.name} | {self.size}'
        return name


class Schedule(models.Model):
    year = models.IntegerField()
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    drivers = models.ManyToManyField(Driver)
    hills = models.ManyToManyField(Hill)
    def __str__(self):
        name = f'{self.station} {self.year}'
        return name
    

class DailySchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    pending = models.BooleanField(default=False)
    date = models.DateField() # year should be the same as schedule
    def __str__(self):
        return f'{self.date} {self.schedule.station} x {self.pending}'    


class Transportation(models.Model):
    ratte = models.ForeignKey(User, on_delete=models.CASCADE)
    daily_schedule = models.ForeignKey(DailySchedule, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    hill = models.ForeignKey(Hill, on_delete=models.CASCADE)
    arrival_time = models.TimeField(default=datetime.now)
    container_size = models.FloatField()
    saved = models.BooleanField(default=False)
    

#################################### Manager ####################################
    
class YearlyGasCharge(models.Model):
    year = models.IntegerField(unique=True)
    gas_charge = models.FloatField(choices=[(r,r) for r in range(-99, 100)])
    def __str__(self):
        return f'{self.year} {self.gas_charge}'


class YearlyStationExport(models.Model):
    year = models.IntegerField()
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    total_tons = models.FloatField(default=0)
    density = models.FloatField(default=0)
    total_volume = models.FloatField(default=0)
    def __str__(self):
        return f'{self.year} {self.station}'


class YearlyDistancePrice(models.Model):
    year = models.IntegerField()
    distance = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    def __str__(self):
        return f'{self.year} {self.distance}km: {self.price} CHF/t'


class YearlyHillStationDistance(models.Model):
    year = models.IntegerField()
    # station = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True)
    hill = models.ForeignKey(Hill, on_delete=models.CASCADE)
    distance = models.IntegerField(default=0)    
    def __str__(self):
        return f'{self.year} {self.hill} {self.distance}km'

