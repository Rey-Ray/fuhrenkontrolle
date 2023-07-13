# fuhrenkontrolle
## Data Format:
at the main forlder (where manage.py exists), there should be a folder named 'data'. in this directory there should exist csv files by these names:

drivers/
farmers&hills/
stations

the first row is the header of each coloumn:

stations: Year, Name
year is just at the first row.

drivers: Station, Name, Locatoin
Name is the driver or the company name.

farmers_hills: Station, Name, Size
Name is the farmers name.

If a driver works for several station, it should has several rows, one for each station.




