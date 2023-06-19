from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('schedule/selection/', views.schedule_selection_view, name='schedule_selection'), # can define a name
    path('schedule/save/', views.save_schedule_view, name='save_schedule'),
    path('schedule/<daily_id>/', views.schedule_view, name='schedule'),
    path('manager/schedule/selection/', views.manager_schedules_view, name='manager_schedule_selection'),
    path('parameter/', views.parameter_view, name='parameter'),
    path('parameter/<year>/', views.parameter_year_view, name='parameter_year'),
    path('gas-charge/<year>/', views.gas_charge_view, name='gas_charge'),    
    path('distance-price/<year>/', views.distance_price_view, name='distance_price'),
    path('stations-exports/<year>/', views.stations_exports_view, name='stations_exports'),
    path('hill-distance/<year>/', views.hill_station_distance_view, name='hill_distance'),
    path('receipt/', views.receipt_view, name='receipt')
]