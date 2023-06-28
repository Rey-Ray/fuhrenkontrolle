import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import DateStationForm, ScheduleForm, TransportationForm, YearlyDistancePriceForm, YearlyStationExportForm, YearForm, YearlyGasChargeForm, YearlyHillStationDistanceForm, ReceiptForm
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
    if request.method == 'POST':
        form = YearForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            return redirect('parameter_year', year=year)
    else:
        form = YearForm()
    return render(request, 'parameter.html', {'form':form})

@manager_required
@set_role
def parameter_year_view(request, year):
    form = YearForm(initial={'year': year})
    return render(request, 'parameter.html', {'form': form, 'year': year})


@manager_required
@set_role
def distance_price_view(request, year):
    if request.method == 'POST':
        form = YearlyDistancePriceForm(request.POST)
        if form.is_valid():
            distance = form.cleaned_data['distance']
            price = form.cleaned_data['price']
            try:
                ydp_obj = YearlyDistancePrice.objects.get(year=year, distance=distance)
                # if ydp_obj:
                ydp_obj.price = price
                ydp_obj.save()
                # messages.info(request, f"Gas charge for {year} is set to {charge}")
            except:
                YearlyDistancePrice.objects.create(year=year, distance=distance, price=price)
            # return redirect('schedule', daily_id=daily_id)
    else:
        form = YearlyDistancePriceForm()

    all_distance_price = YearlyDistancePrice.objects.filter(year=year).order_by('distance')

    context = {
        'form': form,
        'all_dp': all_distance_price
        }
    return render(request, 'distance_price.html', context)

@manager_required
@set_role
def stations_exports_view(request, year):
    if request.method == "POST":
        form = YearlyStationExportForm(request.POST)
        if form.is_valid():
            station = form.cleaned_data['station']
            export = form.cleaned_data['export']
            density = form.cleaned_data['density']
            try:
                yse_obj = YearlyStationExport.objects.get(year=year, station=station)
                yse_obj.density = density
                yse_obj.total_tons = export
                yse_obj.save()
            except:
                YearlyStationExport.objects.create(year=year, station=station, total_tons=export, density=density)
    else:
        form = YearlyStationExportForm()
    all_se = YearlyStationExport.objects.filter(year=year).order_by('station')
    return render(request, "stations_exports.html", {'form': form, 'all_se': all_se})

@manager_required
@set_role
def hill_station_distance_view(request, year):
    if request.method == "POST":
        form = YearlyHillStationDistanceForm(request.POST)
        if form.is_valid():
            hill = form.cleaned_data['hill']
            distance = form.cleaned_data['distance']
            try:
                yhd_obj = YearlyHillStationDistance.objects.get(year=year, hill=hill)
                yhd_obj.distance = distance
                yhd_obj.hill = hill
                yhd_obj.save()
            except:
                YearlyHillStationDistance.objects.create(year=year, hill=hill, distance=distance)
    else:
        form = YearlyHillStationDistanceForm()
    all_hsd = YearlyHillStationDistance.objects.filter(year=year)#.order_by('hill')
    return render(request, "hill_distance.html", {'form': form, 'all_hsd': all_hsd})

@manager_required
@set_role
def gas_charge_view(request, year):
    # gas_charge = YearlyGasCharge.objects.get(year=year)
    if request.method == "POST":
        form = YearlyGasChargeForm(request.POST)
        if form.is_valid():
            charge = form.cleaned_data['gas_charge']
            try:
                gas_charge = YearlyGasCharge.objects.get(year=year)
                gas_charge.gas_charge = charge
                gas_charge.save()
                messages.info(request, f"Gas charge for {year} is set to {charge}")
            except:
                YearlyGasCharge.objects.create(year=year, gas_charge=charge)
            return redirect('parameter_year', year=year)
    else:
        form = YearlyGasChargeForm()

    return render(request, "gas_charge.html", {'form': form, 'year': year})

@manager_required
@set_role
def receipt_view(request):
    if request.method == "POST":
        form = ReceiptForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            driver = form.cleaned_data['driver']

            driver_trps = Transportation.objects.filter(driver=driver, daily_schedule__schedule__year=year)
            try:
                gas_charge = YearlyGasCharge.objects.get(year=year)
            except:
                messages.info(request, f"Please in parameter page, enter the Gas charge for the year {year} if it is not zero.")    
                return redirect('receipt')
            total_price = 0
            prices = []
            for trp in driver_trps:
                #transfered Kg:
                trp_station = trp.daily_schedule.schedule.station
                try:
                    yse_obj = YearlyStationExport.objects.get(year=year, station=trp_station)
                except:
                    messages.info(request, f"Please in parameter page, enter yearly station export.")    
                    return redirect('receipt')
                try:
                    hsd_obj = YearlyHillStationDistance.objects.get(year=year, hill=trp.hill)
                except:
                    messages.info(request, f"Please in parameter page, for the hill {trp.hill}, enter the distance to the related station.")    
                    return redirect('receipt')
                try:
                    ydp_obj = YearlyDistancePrice.objects.get(year=year, distance=hsd_obj.distance)
                except:
                    messages.info(request, f"Please in parameter page, set distance.")
                
                    return redirect('receipt')
                trp_price = ydp_obj.price*yse_obj.density*trp.container_size
                total_price += trp_price
                prices.append( (trp.hill, hsd_obj.distance, ydp_obj.price, yse_obj.density, trp.container_size, trp_price) )
            gas_tax = total_price*gas_charge.gas_charge
            final_price = gas_tax*total_price
            return render(request, "receipt.html", {'form': form, 'driver': driver, 'prices': prices, 'gas_tax': gas_tax, 'total_price': total_price, 'final_price': final_price})
    else:
        form = ReceiptForm()
    return render(request, "receipt.html", {'form': form})#, 'driver_trp':driver_trps})


