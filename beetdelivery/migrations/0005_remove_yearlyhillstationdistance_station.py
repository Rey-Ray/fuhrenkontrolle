# Generated by Django 4.2 on 2023-06-14 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beetdelivery', '0004_alter_yearlygascharge_gas_charge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='yearlyhillstationdistance',
            name='station',
        ),
    ]