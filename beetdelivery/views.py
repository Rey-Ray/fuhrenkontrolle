from django.db.models import Sum
from collections import defaultdict
import datetime
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.edit import DeleteView, UpdateView
import json
from django.utils import timezone
from .decorators import manager_required, set_role
from .forms import (DateStationForm, ReceiptForm, TransportationForm, YearForm,
                    YearlyDistancePriceForm, YearlyGasChargeForm,
                    YearlyHillStationDistanceForm, YearlyStationExportForm, CurrencyForm)
from .models import (DailySchedule, Driver, Farmer, Hill, Schedule, Station,
                     Transportation, YearlyDistancePrice, YearlyGasCharge,
                     YearlyHillStationDistance, YearlyStationExport)

import time


def home(request):
    return redirect('schedule_selection')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('schedule_selection')
        else:
            messages.error(request, "Invalid username or password")
            redirect('login')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@set_role
def schedule_selection_view(request):
    if request.is_manager:
        return redirect('manager_schedule_selection')
    pending_schedule = DailySchedule.objects.filter(pending=True, transportation__ratte=request.user).first()
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
                daily_obj.pending = True
                daily_obj.save()

            except Schedule.DoesNotExist:
                messages.error(request, "No hills are planned to be transfered to this station in this year")
                return redirect('schedule_selection')

            return redirect('schedule', daily_id=daily_obj.id)         
    else:
        form = DateStationForm()
    return render(request, 'select_date_station.html', {'form': form})


@login_required
@set_role
def select_farmer_driver_view(request, daily_id):
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
        transportations = Transportation.objects.filter(daily_schedule=daily_id).all().order_by('-id')        
        if transportations:
            latest_hill = transportations.first().hill
        else:
            latest_hill = None
        form = TransportationForm(daily_schedule=daily_obj,  initial={'hill': latest_hill})
    recent_drivers = [x.driver for x in transportations.model.objects.filter(daily_schedule=daily_obj)]
    context = {
        'form': form,
        'transportations': transportations,
        'schedule': daily_obj,  
        }
    return render(request, 'select_farmer_driver.html', context)


def get_latest_container_size_view(request):
    try:
        selected_driver = request.GET.get('driver')
        latest_container_size = Transportation.objects.filter(driver__id=selected_driver).order_by('-id').values_list('container_size', flat=True).first()
        if not latest_container_size:
            latest_container_size = Driver.objects.get(id=selected_driver).container_size
        return JsonResponse({'latest_container_size': latest_container_size})
    except Exception as e:
        print(f"Error {e}")
        return JsonResponse({'error': 1})


def delete_trp_view(request, trp_id):
    trp = Transportation.objects.get(pk=trp_id)
    trp.delete()
    return redirect('schedule', daily_id=trp.daily_schedule.id)


def edit_trp_view(request, trp_id):
    trp = get_object_or_404(Transportation, id=trp_id)
    if request.method == 'POST':
        edit_form = TransportationForm(request.POST, instance=trp)
        if edit_form.is_valid():
            edit_form.save()
            return redirect('schedule', daily_id=trp.daily_schedule.id)
    else:
        edit_form = TransportationForm(instance=trp)
    return render(request, 'edit_transportation_form.html', {'edit_form': edit_form, 'trp_id': trp.id})


@login_required
@set_role
def save_schedule_view(request):
    if request.method == 'POST':
        schedule_id = request.POST['schedule_id']
        schedule = DailySchedule.objects.get(id=schedule_id)
        transportations = Transportation.objects.filter(daily_schedule=schedule_id)
        user_is_ratte = transportations.filter(ratte=request.user).exists()
        if transportations.exists() and user_is_ratte:
            schedule.pending = False
            schedule.save()
        else:
            schedule.delete()
        return redirect('schedule_selection')
    
    
###########################################
# Manager views:

def chosen_year(request):
    try:
        year = request.session.get('year', timezone.now().year)
    except:
        year = timezone.now().year
    return year


@manager_required
@set_role
def manager_schedules_view(request):
    year = chosen_year(request)
    schedules = Schedule.objects.filter(year=year)
    daily_schedules = [sch.dailyschedule_set.all() for sch in schedules]
    return render(request, 'manager_schedules.html', {'schedules':daily_schedules, 'year':year})


@manager_required
@set_role
def select_year_view(request):
    year = chosen_year(request)
    if request.method == 'POST':
        form = YearForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            request.session['year'] = year
            return redirect('select_year')
    else:
        form = YearForm(initial={'year': year})
    return render(request, 'select_year.html', {'form':form, 'year':year})


@manager_required
@set_role
def parameter_view(request):
    year = chosen_year(request)
    return render(request, 'parameter.html', {'year': year})


@manager_required
@set_role
def parameter_year_view(request, year):
    form = YearForm()
    return render(request, 'parameter.html', {'form': form, 'year': year})


@manager_required
@set_role
def currency_selection(request, year):
    if request.method == 'POST':
        form = CurrencyForm(request.POST)
        if form.is_valid():
            selected_currency = form.cleaned_data['currency']            
            return redirect('distance_price', currency=selected_currency)
    else:
        form = CurrencyForm()
    return render(request, 'currency_selection.html', {'form': form})


@manager_required
@set_role
def distance_price_view(request, currency):
    year = chosen_year(request)
    if request.method == 'POST':
        form = YearlyDistancePriceForm(request.POST)
        if form.is_valid():
            distance = form.cleaned_data['distance']
            price = form.cleaned_data['price']
            try:
                ydp_obj = YearlyDistancePrice.objects.get(year=year, distance=distance, currency=currency)
                ydp_obj.price = price
                ydp_obj.save()
                # messages.info(request, f"Gas charge for {year} is set to {charge}")
            except:
                YearlyDistancePrice.objects.create(year=year, distance=distance, price=price, currency=currency)
            # return redirect('schedule', daily_id=daily_id)
    else:
        form = YearlyDistancePriceForm()
    all_distance_price = YearlyDistancePrice.objects.filter(year=year, currency=currency).order_by('distance')
    context = {
        'form': form,
        'all_dp': all_distance_price,
        'year': year,
        'currency': currency
        }
    return render(request, 'distance_price.html', context)


def edit_dp_view(request, dp_id):
    dp = get_object_or_404(YearlyDistancePrice, id=dp_id)
    print("====== ", dp)
    if request.method == 'POST':
        edit_form = YearlyDistancePriceForm(request.POST, initial={'distance':dp.distance, 'price':dp.price})
        if edit_form.is_valid():
            dp.distance = int(request.POST['distance'][0])
            dp.price = float(request.POST['price'][0])
            dp.save()
            return redirect('distance_price', currency=dp.currency)
    else:
        edit_form = YearlyDistancePriceForm(initial={'distance':dp.distance, 'price':dp.price})
    return render(request, 'edit_dp.html', {'edit_form': edit_form, 'dp_id': dp.id})


def delete_dp_view(request, dp_id):
    dp = YearlyDistancePrice.objects.get(pk=dp_id)
    dp.delete()
    year = chosen_year(request)
    return redirect('distance_price', year)


@manager_required
@set_role
def stations_exports_view(request, year):
    if request.method == "POST":
        form = YearlyStationExportForm(request.POST)
        if form.is_valid():
            station = form.cleaned_data['station']
            export_t = form.cleaned_data['export']
            schedules = Schedule.objects.filter(station=station, year=year)
            total_volume = 0
            for schedule in schedules:
                daily_schedules = DailySchedule.objects.filter(schedule=schedule)
                for daily_schedule in daily_schedules:
                    total_volume += Transportation.objects.filter(daily_schedule=daily_schedule).aggregate(Sum('container_size'))['container_size__sum'] or 0
            export_kg = export_t*1000
            density = round(export_kg / total_volume,2) if total_volume > 0 else -1
            try:
                yse_obj = YearlyStationExport.objects.get(year=year, station=station)
                yse_obj.total_tons = export_t
                yse_obj.density = density
                yse_obj.total_volume = total_volume
                yse_obj.save()
            except:
                YearlyStationExport.objects.create(year=year, station=station, total_tons=export_t, density=density, total_volume=total_volume)
    else:
        form = YearlyStationExportForm()
    all_se = YearlyStationExport.objects.filter(year=year).order_by('station')
    return render(request, "stations_exports.html", {'form': form, 'all_se': all_se, 'year':year})


def edit_se_view(request, se_id):
    se = get_object_or_404(YearlyStationExport, id=se_id)
    if request.method == 'POST':
        station = get_object_or_404(Station, id=se.station.id)
        edit_form = YearlyStationExportForm(request.POST, initial={'station': station.station_name, 'export': se.total_tons})
        if edit_form.is_valid():
            se.station.id = int(request.POST['station'][0])
            se.total_tons = float(request.POST['export'][0])
            se.save()
            year = se.year
            return redirect('stations_exports', year)
    else:
        edit_form = YearlyStationExportForm(initial={'station':se.station, 'export':se.total_tons})
    return render(request, 'edit_se.html', {'edit_form': edit_form, 'se_id': se.id})


def delete_se_view(request, se_id):
    se = YearlyStationExport.objects.get(pk=se_id)
    se.delete()
    year = chosen_year(request)
    return redirect('stations_exports', year)


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
    all_hsd = YearlyHillStationDistance.objects.filter(year=year)
    return render(request, "hill_distance.html", {'form': form, 'all_hsd': all_hsd, 'year': year})


def edit_hd_view(request, hd_id):
    hd = get_object_or_404(YearlyHillStationDistance, id=hd_id)
    if request.method == 'POST':
        edit_form = YearlyHillStationDistanceForm(request.POST, initial={'hill':hd.hill, 'distance':hd.distance})
        if edit_form.is_valid():
            hd.distance = int(request.POST['distance'])
            hill = get_object_or_404(Hill, id=int(request.POST['hill']))
            hd.hill = hill
            hd.save()
            year = hd.year
            return redirect('hill_distance', year)
    else:
        edit_form = YearlyHillStationDistanceForm(initial={'hill':hd.hill, 'distance':hd.distance})
    return render(request, 'edit_hd.html', {'edit_form': edit_form, 'hd_id': hd.id})


def delete_hd_view(request, hd_id):
    hd = YearlyHillStationDistance.objects.get(pk=hd_id)
    hd.delete()
    year = chosen_year(request)
    return redirect('hill_distance', year)


@manager_required
@set_role
def gas_charge_view(request, year):
    if request.method == "POST":
        form = YearlyGasChargeForm(request.POST)
        if form.is_valid():
            charge = form.cleaned_data['gas_charge']
            try:
                gas_charge = YearlyGasCharge.objects.get(year=year)
                gas_charge.gas_charge = charge
                gas_charge.save()
                g_c =gas_charge.gas_charge
                # messages.info(request, f"Gas charge for {year} is set to {charge}%")
            except:
                gas_charge = YearlyGasCharge.objects.create(year=year, gas_charge=charge)
                g_c = gas_charge.gas_charge
    else:
        form = YearlyGasChargeForm()
        try:
            gas_charge = YearlyGasCharge.objects.get(year=year)
            g_c = gas_charge.gas_charge
        except:
            g_c = 0
    return render(request, "gas_charge.html", {'form': form, 'year': year, 'gas_charge': g_c})


@manager_required
@set_role
def receipt_view(request):
    year = chosen_year(request)
    if request.method == "POST":
        form = ReceiptForm(request.POST)
        if form.is_valid():
            driver = form.cleaned_data['driver']
            receipt_station = form.cleaned_data['station']
            if receipt_station == None:
                driver_trps = Transportation.objects.filter(driver=driver, daily_schedule__schedule__year=year)
            else:
                driver_trps = Transportation.objects.filter(driver=driver, daily_schedule__schedule__year=year,  daily_schedule__schedule__station=receipt_station)
            try:
                gas_charge = YearlyGasCharge.objects.get(year=year)
                gas_charge = gas_charge.gas_charge
            except:
                messages.info(request, f"Please in the Parameter, enter the Gas charge for the year {year}")    
                return redirect('receipt')

            total_price = 0
            total_trp_quantity = 0
            num_total_trp = 0
            prices_dict = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0, 0])
            prices = []
            for trp in driver_trps:
                num_total_trp += 1
                trp_station = trp.daily_schedule.schedule.station
                try:
                    yse_obj = YearlyStationExport.objects.get(year=year, station=trp_station)
                except:
                    messages.info(request, f"In parameter page, enter the exported amount of station {trp_station}")    
                    # return redirect('receipt')
                try:
                    hsd_obj = YearlyHillStationDistance.objects.get(year=year, hill=trp.hill)
                    try:
                        ydp_obj = YearlyDistancePrice.objects.get(year=year, distance=hsd_obj.distance)
                    except:
                        messages.info(request, f"In parameter page, set price for distance {hsd_obj.distance} km")
                        # return redirect('receipt')
                except:
                    messages.info(request, f"In parameter page, for the hill {trp.hill}, enter the distance to the related station")    
                    # return redirect('receipt')
                distance = ydp_obj.distance
                distance_price = ydp_obj.price
                container_size = trp.container_size
                total_trp_quantity += container_size
                hill = trp.hill
                station_export = yse_obj.total_tons
                station_density_t = yse_obj.density /1000
                trp_price = round(distance_price * station_density_t * container_size, 2)
                total_price += trp_price
                key = (hill, container_size, distance_price)
                prices_dict[key][5] += 1
                num_same_trp = prices_dict[key][5]
                price_sum_trps =  trp_price * num_same_trp
                total_quantity = container_size * num_same_trp
                prices_dict[key][0:5] = [hill, distance, distance_price, station_export, container_size]
                prices_dict[key][6:8] = [total_quantity, price_sum_trps]
            prices = [tuple(values) for values in prices_dict.values()]
            total_price = round(total_price,2)
            gas_charge_num = gas_charge/100
            gas_tax = round(total_price * gas_charge_num, 2)
            final_price = round(total_price - gas_tax, 2)
            return render(request, "receipt.html", {'form': form, 'year': year, 'driver': driver, 'prices': prices, 'gas_tax': gas_tax, 'total_price': total_price, 'final_price': final_price, 'gas_charge': gas_charge, 'total_trp_quantity':total_trp_quantity, 'num_total_trp':num_total_trp})
    else:
        form = ReceiptForm()
    return render(request, "receipt.html", {'form': form, 'year': year})


def driver_search(request):
    query = request.GET.get('query', '')
    drivers = list(Driver.objects.filter(name__icontains=query).values_list('name', flat=True))
    return JsonResponse(drivers, safe=False)