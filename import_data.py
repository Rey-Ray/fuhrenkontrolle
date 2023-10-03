import zipfile
import shutil
import os
import django
import pandas as pd

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driversWebApp.settings')
django.setup()

from beetdelivery.models import Farmer, Hill, Station, Driver, Schedule, YearlyHillStationDistance


def read_data_zip(zip_file_path):
    extracted_dir = '/tmp/extracted_data'
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        if os.path.exists(extracted_dir):
            shutil.rmtree(extracted_dir)
        zip_ref.extractall(extracted_dir)
    return


def import_excels_data():
    data_path = '/tmp/extracted_data/'
    file_list = os.listdir(data_path)
    # Find the year
    try:
        yf = [file for file in file_list if file.startswith('Trans')][0]
        year = yf.split(' ')[-1].split('.')[0]
        print('importing data of year', year)
    except:
        print('related year of the data is not defined')
        return
    
    for f in file_list:
        if f.startswith("Distanzen"):
            name_list = f.split('.')
            station_name = name_list[0][10:-3].strip()
            print(station_name)
            station, _ = Station.objects.get_or_create(station_name=station_name)
    for f in file_list:    
        if f.startswith("Distanzen"):
            name_list = f.split('.')
            station_name = name_list[0][10:-3].strip()
            station, _ = Station.objects.get_or_create(station_name=station_name)
            Schedule.objects.filter(year=year, station=station).delete()
            schedule, _ = Schedule.objects.get_or_create(year=year, station=station)
            import_farmers_hills_distances(data_path+f, schedule, year)
        elif f.startswith("Transporte"):
             import_drivers(data_path+f, year)
    return 


def import_farmers_hills_distances(farmers_hills_excel_file, schedule, year):
    # adding farmers and hills
    farmers_hills = pd.read_excel(farmers_hills_excel_file)
    for index, row in farmers_hills.iterrows():
        farmer_name = row['Schlagname']
        hill_size = row['Schlaggröße'].replace(',','.')
        farmer = Farmer.objects.filter(name=farmer_name).first()
        if not farmer:
            farmer = Farmer.objects.create(name=farmer_name)
            # print(f"Added farmer: {farmer.name}")
        hill = Hill.objects.filter(farmer=farmer, size=hill_size).first()
        if not hill:
            hill = Hill.objects.create(farmer=farmer, size=hill_size)
            # print(f"Added hill: {hill.farmer} - {hill.size}")
        schedule.hills.add(hill)
        distance = row['Distanz']
        hill_distance = YearlyHillStationDistance.objects.filter(hill=hill, year=year).first()
        if hill_distance:
            hill_distance.distance = distance
        else:
            hill_distance = YearlyHillStationDistance.objects.create(distance=distance, hill=hill, year=year)
            # print(f"Added hill_distance: {hill.farmer} - {hill.size}, {hill_distance.distance}")
    return


def import_drivers(drivers_excel_file, year):
    # adding drivers
    driver_station = pd.read_excel(drivers_excel_file)
    for index, row in driver_station.iterrows():
        driver_name = str(row['Bezeichnung']).strip()
        if not driver_name or driver_name=='nan':
            continue
        driver_location = str(row['Wohnort']).strip()
        if not driver_location:
            driver_location = '_'
        driver_container_size = str(row['Volume'.strip()]).strip().replace(',','.')
        if not driver_container_size or not driver_container_size.isnumeric():
            driver_container_size = '0'  
        driver_container_size = float(driver_container_size)
        driver = Driver.objects.filter(name=driver_name, location=driver_location, container_size=driver_container_size).first()    
        if not driver:
            driver = Driver.objects.create(name=driver_name, location=driver_location, container_size=driver_container_size)
            # print(f"Added driver: {driver.name} - {driver.location}")

        station_name = str(row['Verladestation']).strip()
        try:
            
            station = Station.objects.get(station_name=station_name)
            schedule, _ = Schedule.objects.get_or_create(year=year, station=station)
            schedule.drivers.add(driver)
        except Exception as e:
            print(f"-- {e} - {station_name}")
    return


if __name__ == '__main__':
    read_data_zip('/home/reyhaneh/Desktop/data.zip')
    import_excels_data()