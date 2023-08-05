
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('schedule/selection/', views.schedule_selection_view, name='schedule_selection'),
    path('schedule/save/', views.save_schedule_view, name='save_schedule'),
    path('schedule/<daily_id>/', views.select_farmer_driver_view, name='schedule'),
    path('get-latest-container-size/', views.get_latest_container_size_view, name='get_latest_container_size'),
    path('trp-edit/<int:trp_id>/', views.edit_trp_view, name='edit_trp'),
    path('trp-delete/<int:trp_id>/', views.delete_trp_view, name='delete_trp'),
    path('manager/schedule/selection/', views.manager_schedules_view, name='manager_schedule_selection'),
    path('select-year/', views.select_year_view, name='select_year'),
    path('parameter/', views.parameter_view, name='parameter'),
    path('parameter/<year>/', views.parameter_year_view, name='parameter_year'),
    path('gas-charge/<year>/', views.gas_charge_view, name='gas_charge'),    
    path('distance-price/<year>/', views.distance_price_view, name='distance_price'),
    path('dp-edit/<int:dp_id>/', views.edit_dp_view, name='edit_dp'),
    path('dp-delete/<int:dp_id>/', views.delete_dp_view, name='delete_dp'),
    path('stations-exports/<year>/', views.stations_exports_view, name='stations_exports'),
    path('se-delete/<int:se_id>/', views.delete_se_view, name='delete_se'),
    path('hill-distance/<year>/', views.hill_station_distance_view, name='hill_distance'),
    path('hd-delete/<int:hd_id>/', views.delete_hd_view, name='delete_hd'),    
    path('receipt/', views.receipt_view, name='receipt'),
    path('api/driver_search/', views.driver_search, name='driver_search'),
    path('edit/<int:dp_id>/', views.edit_dp_view, name='editor'),
]