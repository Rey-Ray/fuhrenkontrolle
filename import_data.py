import pandas as pd
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driversWebApp.settings')
django.setup()

from beetdelivery.models import Farmer, Hill, Station, Driver, Schedule 

def import_data():
    drivers_csv_file = 'data/drivers.csv'
    hills_csv_file = 'data/farmers_hills.csv'
    stations_csv_file = 'data/stations.csv'


    # adding stations
    sf = pd.read_csv(stations_csv_file)
    for index, row in sf.iterrows():
        Station_name = row['Name']

        existing_station = Station.objects.filter(station_name=Station_name).first()
        if existing_station:
            station = existing_station
            print(f"Station already exists: {station.station_name}")
        else:
            station = Station.objects.create(station_name=Station_name)
            print(f"Added station: {station.station_name}")

    year = int(sf.iloc[0, 0])

    # adding drivers
    df = pd.read_csv(drivers_csv_file)
    for index, row in df.iterrows():
        driver_station = row['Station']
        driver_name = row['Name']
        driver_location = row['Location']
        driver_container_size = row['Container_size']

        # Check if a driver with the same name and location already exists
        existing_driver = Driver.objects.filter(name=driver_name, location=driver_location, container_size=driver_container_size).first()
        if existing_driver:
            driver = existing_driver
            print(f"Driver already exists: {driver.name} - {driver.location}")
        else:
            driver = Driver.objects.create(name=driver_name, location=driver_location, container_size=driver_container_size)
            print(f"Added driver: {driver.name} - {driver.location}")

        station, created = Station.objects.get_or_create(station_name=driver_station)
        schedule, created = Schedule.objects.get_or_create(year=year, station=station)
        schedule.drivers.add(driver)

        


    # adding farmers and hills
    hf = pd.read_csv(hills_csv_file)
    for index, row in hf.iterrows():
        farmer_name = row['Name']
        hill_size = row['Size']
        hill_station = row['Station']

        existing_farmer = Farmer.objects.filter(name=farmer_name).first()
        if existing_farmer:
            farmer = existing_farmer
            print(f"Farmer already exists: {farmer.name}")
            farmer = existing_farmer
        else:
            farmer = Farmer.objects.create(name=farmer_name)
            print(f"Added farmer: {farmer.name}")

        existing_hill = Hill.objects.filter(farmer=farmer, size=hill_size).first()
        if existing_hill:
            hill = existing_hill
            print(f"Hill already exists: {hill.farmer} - {hill.size}")
        else:
            hill = Hill.objects.create(farmer=farmer, size=hill_size)
            print(f"Added hill: {hill.farmer} - {hill.size}")

        station, created = Station.objects.get_or_create(station_name=hill_station)
        schedule, created = Schedule.objects.get_or_create(year=year, station=station)
        schedule.hills.add(hill)

    
    
    print('Data import completed.')


if __name__ == '__main__':
    import_data()
