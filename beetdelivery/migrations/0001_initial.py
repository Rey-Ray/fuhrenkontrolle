# Generated by Django 4.2.2 on 2023-07-13 03:00

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DailySchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pending', models.BooleanField(default=False)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('location', models.CharField(blank=True, max_length=50, null=True)),
                ('container_size', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Farmer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Hill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=50)),
                ('farmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beetdelivery.farmer')),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='YearlyDistancePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('distance', models.IntegerField(default=0)),
                ('price', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='YearlyGasCharge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(unique=True)),
                ('gas_charge', models.FloatField(choices=[(-99, -99), (-98, -98), (-97, -97), (-96, -96), (-95, -95), (-94, -94), (-93, -93), (-92, -92), (-91, -91), (-90, -90), (-89, -89), (-88, -88), (-87, -87), (-86, -86), (-85, -85), (-84, -84), (-83, -83), (-82, -82), (-81, -81), (-80, -80), (-79, -79), (-78, -78), (-77, -77), (-76, -76), (-75, -75), (-74, -74), (-73, -73), (-72, -72), (-71, -71), (-70, -70), (-69, -69), (-68, -68), (-67, -67), (-66, -66), (-65, -65), (-64, -64), (-63, -63), (-62, -62), (-61, -61), (-60, -60), (-59, -59), (-58, -58), (-57, -57), (-56, -56), (-55, -55), (-54, -54), (-53, -53), (-52, -52), (-51, -51), (-50, -50), (-49, -49), (-48, -48), (-47, -47), (-46, -46), (-45, -45), (-44, -44), (-43, -43), (-42, -42), (-41, -41), (-40, -40), (-39, -39), (-38, -38), (-37, -37), (-36, -36), (-35, -35), (-34, -34), (-33, -33), (-32, -32), (-31, -31), (-30, -30), (-29, -29), (-28, -28), (-27, -27), (-26, -26), (-25, -25), (-24, -24), (-23, -23), (-22, -22), (-21, -21), (-20, -20), (-19, -19), (-18, -18), (-17, -17), (-16, -16), (-15, -15), (-14, -14), (-13, -13), (-12, -12), (-11, -11), (-10, -10), (-9, -9), (-8, -8), (-7, -7), (-6, -6), (-5, -5), (-4, -4), (-3, -3), (-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
            ],
        ),
        migrations.CreateModel(
            name='YearlyStationExport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('total_tons', models.FloatField(default=0)),
                ('density', models.FloatField(default=0)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beetdelivery.station')),
            ],
        ),
        migrations.CreateModel(
            name='YearlyHillStationDistance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('distance', models.IntegerField(default=0)),
                ('hill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beetdelivery.hill')),
            ],
        ),
        migrations.CreateModel(
            name='Transportation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrival_time', models.TimeField(default=datetime.datetime.now)),
                ('container_size', models.FloatField()),
                ('saved', models.BooleanField(default=False)),
                ('daily_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beetdelivery.dailyschedule')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beetdelivery.driver')),
                ('hill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beetdelivery.hill')),
                ('ratte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('drivers', models.ManyToManyField(to='beetdelivery.driver')),
                ('hills', models.ManyToManyField(to='beetdelivery.hill')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beetdelivery.station')),
            ],
        ),
        migrations.CreateModel(
            name='Ratte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default='ratte', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default='manager', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='dailyschedule',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beetdelivery.schedule'),
        ),
    ]
