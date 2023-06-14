import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import DateStationForm, ScheduleForm, TransportationForm, YearlyDistancePriceForm, YearlyStationExportFormset, YearlyStationExportForm, YearlyHillStationDistanceFormset, YearForm
from .models import Driver, Farmer, Hill, Schedule, Station, Transportation, YearlyDistancePrice, YearlyStationExport, YearlyHillStationDistance, DailySchedule, YearlyGasCharge
from .decorators import manager_required, set_role

def home(request):
    return redirect('schedule_selection')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            redirect('login')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@manager_required
@set_role
def manager_schedules_view(request):
    schedules = Schedule.objects.all()
    daily_schedules = [sch.dailyschedule_set.all() for sch in schedules]
    return render(request, 'manager_schedules.html', {'schedules':daily_schedules})


@login_required
@set_role
def schedule_selection_view(request):
    if request.is_manager:
        return redirect('manager_schedule_selection')
    pending_schedule = DailySchedule.objects.filter(pending=True).first()
    if pending_schedule is not None:
        return redirect('schedule', daily_id=pending_schedule.id)
        
    if request.method == 'POST':
        form = DateStationForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            station = form.cleaned_data['station']
            year = date.year
            try:
                schedule_obj = Schedule.objects.get(year=year, station=station)
                daily_obj = DailySchedule.objects.get_or_create(schedule=schedule_obj, date=date)[0]
                print(daily_obj)
                daily_obj.pending = True
                daily_obj.save()
            except Schedule.DoesNotExist:
                # print("Could not find schedule")
                messages.error(request, "No hills are planned to be transfered to this station in this year!")
                return redirect('schedule_selection')

            return redirect('schedule', daily_id=daily_obj.id)         
    else:
        form = DateStationForm()
    return render(request, 'select_date_station.html', {'form': form})

@login_required
@set_role
def schedule_view(request, daily_id):
    daily_obj = DailySchedule.objects.get(id=daily_id)
    user = request.user
    if request.method == 'POST':
        form = TransportationForm(request.POST, daily_schedule=daily_obj)
        if form.is_valid():
            transportation = form.save(commit=False)
            transportation.ratte = user
            transportation.save()
            return redirect('schedule', daily_id=daily_id)
    else:
        form = TransportationForm(daily_schedule=daily_obj)

    transportations = Transportation.objects.filter(daily_schedule=daily_id).all()
    # TransportationFormSet = modelformset_factory(Transportation, form=TransportationForm, extra=0)
    
    context = {
        'form': form,
        'transportations': transportations,
        'schedule': daily_obj
        }
    return render(request, 'select_farmer_driver.html', context)

@login_required
@set_role
def save_schedule_view(request):
    if request.method == 'POST':
        schedule = DailySchedule.objects.get(id=request.POST['schedule_id'])
        schedule.pending = False
        schedule.save()

        return redirect('schedule_selection')
    
@manager_required
@set_role
def parameter_view(request):
    year = datetime.datetime.now().year
    user = request.user
    #numbers = range(1,71)
    if request.method == 'POST':
        form = YearForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            gas_charge = form.cleaned_data['gas_charge']
            
            # Check if a Year instance already exists with the given year
            yearly_gas_charge = YearlyGasCharge.objects.filter(year=year).first()
            
            if yearly_gas_charge:
                yearly_gas_charge.gas_charge = gas_charge
                yearly_gas_charge.save()
            else:
                YearlyGasCharge.objects.create(year=year, gas_charge=gas_charge)
            
            # return redirect('parameter')
        else:
            print(form.errors)
            # form = 
    else:
        form = YearForm()
    
    return render(request, 'parameter.html', {'form':form, 'year': year})
    #return render(request, 'parameter.html', {'year': 2023, 'numbers':numbers, 'is_manager': is_manager})

def distance_price_view(request, year):
    if request.method == "POST":
        distance_price_form = YearlyDistancePriceForm(request.POST)
        print('yoooooooooo')
        if distance_price_form.is_valid():
            for f in distance_price_form.cleaned_data.keys():
                print(f)
                if f.startswith('distance'):
                    print('heeyyyyaaa')
                    price = distance_price_form.cleaned_data[f]
                    km = f.split('_')[-1]
                    ydp = YearlyDistancePrice(distance=km, price=price, year=year)
                    ydp.save()
                    
        return redirect('parameter')    
    else:
        distance_price_form = YearlyDistancePriceForm()

    return render(request, 'distance_price.html', {'distance_price_form': distance_price_form, 'year': year})

def stations_exports_view(request, year):
    stations_exports = YearlyStationExport.objects.filter(year=year)  # replace "your_conditions" with your actual conditions
    if request.method == "POST":
        formset = YearlyStationExportFormset(request.POST, queryset=stations_exports)
        if formset.is_valid():
            formset.save()
    else:
        stations = Station.objects.all()
        for station in stations:
            YearlyStationExport.objects.get_or_create(year=year, station=station)


        formset = YearlyStationExportFormset(queryset=stations_exports)

    return render(request, "stations_exports.html", {'formset': formset})

def hill_station_distance_view(request, year):
    hill_distance = YearlyHillStationDistance.objects.filter(year=year)  # replace "your_conditions" with your actual conditions
    if request.method == "POST":
        formset = YearlyHillStationDistanceFormset(request.POST, queryset=hill_distance)
        if formset.is_valid():
            formset.save()
    else:
        hills = Hill.objects.all()
        for hill in hills:
            YearlyHillStationDistance.objects.get_or_create(year=year, hill=hill)


        formset = YearlyHillStationDistanceFormset(queryset=hill_distance)

    return render(request, "hill_distance.html", {'formset': formset})

#     if request.method == "POST":
#         station_export_form = YearlyStationExportForm(request.POST)
#         print('yoooooooooo')
#         if distance_price_form.is_valid():
#             yearly_charge = Year.objects.get(year=datetime.date(2023,1,1))
#             if not yearly_charge:
#                 yearly_charge = Year(year=datetime.datetime(2023,1,1), gas_charge=6)
#             print("holaaaaaaaaaaaaa")
#             for f in station_export_form.cleaned_data.keys():
#                 print(f)
#                 if f.startswith('distance'):
#                     print('heeyyyyaaa')
#                     price = station_export_form.cleaned_data[f]
#                     km = f.split('_')[-1]
#                     ydp = YearlyDistancePrice(distance=km, price=price, yearly_charge=yearly_charge)
#                     ydp.save()
                    
#         return redirect('parameter')    
#     else:
#         distance_price_form = YearlyDistancePriceForm()

#     return render(request, 'distance_prices.html', {'distance_price_form': distance_price_form})

# @login_required
# def yearly_charges_view(request):
#     user = request.user
#     if not hasattr(user, 'manager'):
#         return redirect('schedule_selection')
#     is_manager = True

#     if request.method == 'POST':
#         yearly_form = YearlyForm(request.POST)
#     else:
#         pass

#     return render(request, 'parameter.html', {'yearly_form': yearly_form})
            

# def choose_year_view(request):
#     if request.method == 'POST':
#         form = YearForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('parameter')
#     else:
#         form = YearForm()
    
#     return render(request, 'choose_year_view.html', {'form':form})
# @login_required
# def get_recipt_view(request, driver_id):
#     user = request.user
#     if not hasattr(user, 'manager'):
#         return redirect('schedule_selection')
#     is_manager = True
    
#     driver = Driver.objects.get(id=driver_id)
#     transportations = driver.transportations.all()
#     recipt = {}
#     for t in transportations:
#         distance = t.distance_price.distance
#         price = t.distance_price.price
