from django.db.models import Sum

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

from .decorators import manager_required, set_role
from .forms import (DateStationForm, ReceiptForm, TransportationForm, YearForm,
                    YearlyDistancePriceForm, YearlyGasChargeForm,
                    YearlyHillStationDistanceForm, YearlyStationExportForm)
from .models import (DailySchedule, Driver, Farmer, Hill, Schedule, Station,
                     Transportation, YearlyDistancePrice, YearlyGasCharge,
                     YearlyHillStationDistance, YearlyStationExport)


def home(request):###############################
    return redirect('schedule_selection')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user: #is not None:
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
                messages.error(request, "No hills are planned to be transfered to this station in this year!")
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
        edit_form = [(trp.id, TransportationForm(daily_schedule=daily_obj, instance=trp)) for trp in transportations]

        if transportations:
            latest_hill = Transportation.objects.filter(ratte=user).order_by('-id').values_list('hill', flat=True).first()
        
        else:
            latest_hill = None
        form = TransportationForm(daily_schedule=daily_obj,  initial={'hill': latest_hill})

    context = {
        'form': form,
        'transportations': transportations,
        'schedule': daily_obj,
        'edit_form': edit_form
        }
    return render(request, 'select_farmer_driver.html', context)


def get_latest_container_size_view(request):
    selected_driver = request.GET.get('driver')
    latest_container_size = Transportation.objects.filter(driver=selected_driver).order_by('-id').values_list('container_size', flat=True).first()
    return JsonResponse({'latest_container_size': latest_container_size})


def delete_trp_view(request, trp_id):
    trp = Transportation.objects.get(pk=trp_id)
    trp.delete()
    return redirect('schedule', daily_id=trp.daily_schedule.id)


def edit_trp_view(request, trp_id):
    trp = get_object_or_404(Transportation, id=trp_id)
    if request.method == 'POST':
        form = TransportationForm(request.POST, instance=trp)
        if form.is_valid():
            form.save()
            return redirect('schedule', daily_id=trp.daily_schedule.id)
    
    edit_form = TransportationForm(instance=trp)#initial={'hill': trp.hill, 'container_size': trp.container_size, 'driver': trp.driver})
    return render(request, 'select_farmer_driver.html', {'edit_form': edit_form, 'schedule': trp.daily_schedule.id})


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
@manager_required
@set_role
def manager_schedules_view(request):
    try:
        year = request.session.get('year', timezone.now().year)
    except:
        year = timezone.now().year

    schedules = Schedule.objects.filter(year=year)
    daily_schedules = [sch.dailyschedule_set.all().order_by('-date') for sch in schedules]
    return render(request, 'manager_schedules.html', {'schedules':daily_schedules, 'year':year})


@manager_required
@set_role
def select_year_view(request):
    if request.method == 'POST':
        form = YearForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            request.session['year'] = year
            messages.info(request, f" Year {year} is selected.")
            return redirect('select_year')
    else:
        try:
            year = request.session.get('year', timezone.now().year)
        except:
            year = timezone.now().year
        form = YearForm(initial={'year': year})
    return render(request, 'select_year.html', {'form':form})

@manager_required
@set_role
def parameter_view(request):
    try:
        year = request.session.get('year', timezone.now().year)
    except:
        year = timezone.now().year
    return render(request, 'parameter.html', {'year': year})


@manager_required
@set_role
def parameter_year_view(request, year):
    form = YearForm()
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
        'all_dp': all_distance_price,
        'year': year
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
            
            schedules = Schedule.objects.filter(station=station, year=year)

            total_volume = 0
            for schedule in schedules:
                daily_schedules = DailySchedule.objects.filter(schedule=schedule)
                for daily_schedule in daily_schedules:
                    total_volume += Transportation.objects.filter(daily_schedule=daily_schedule).aggregate(Sum('container_size'))['container_size__sum'] or 0
            
            # Calculate the density
            density = export / total_volume if total_volume > 0 else 0

            try:
                yse_obj = YearlyStationExport.objects.get(year=year, station=station)
                yse_obj.total_tons = export
                yse_obj.density = density
                yse_obj.save()
            except:
                YearlyStationExport.objects.create(year=year, station=station, total_tons=export, density=density)
    else:
        form = YearlyStationExportForm()
    all_se = YearlyStationExport.objects.filter(year=year).order_by('station')
    return render(request, "stations_exports.html", {'form': form, 'all_se': all_se, 'year':year})


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
    return render(request, "hill_distance.html", {'form': form, 'all_hsd': all_hsd, 'year': year})


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
            # return redirect('parameter_year', year=year)
    else:
        form = YearlyGasChargeForm()
    return render(request, "gas_charge.html", {'form': form, 'year': year})


@manager_required
@set_role
def receipt_view(request):
    try:
        year = request.session.get('year', timezone.now().year)
    except:
        year = timezone.now().year

    if request.method == "POST":
        form = ReceiptForm(request.POST)
        if form.is_valid():
            # year = form.cleaned_data['year']
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
                trp_price = ydp_obj.price*yse_obj.density*trp.container_size/1000
                total_price += trp_price
                prices.append( (trp.hill, hsd_obj.distance, ydp_obj.price, yse_obj.density, trp.container_size, trp_price) )
            gas_tax = total_price*gas_charge.gas_charge
            final_price = gas_tax*total_price
            return render(request, "receipt.html", {'form': form, 'year': year, 'driver': driver, 'prices': prices, 'gas_tax': gas_tax, 'total_price': total_price, 'final_price': final_price})
    else:
        form = ReceiptForm()
    return render(request, "receipt.html", {'form': form, 'year': year})#, 'driver_trp':driver_trps})


