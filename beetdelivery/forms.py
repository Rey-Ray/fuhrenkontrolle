from django import forms
from .models import Farmer, Driver, Station, Schedule, Transportation, YearlyStationExport, YearlyHillStationDistance, YearlyGasCharge, YearlyDistancePrice, Hill
import datetime
from django.utils.safestring import mark_safe
from django_select2.forms import ModelSelect2Widget


class DateStationForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class':'col form-control form-control-lg p-3'}))
    station = forms.ModelChoiceField(queryset=Station.objects.all().order_by('station_name'), widget=forms.Select(attrs={'class':'col form-control form-control-lg p-3'}))


class TransportationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        daily_schedule = kwargs.pop('daily_schedule', None)
        super(TransportationForm, self).__init__(*args, **kwargs)
        if daily_schedule:
            self.instance.daily_schedule = daily_schedule
            self.fields['hill'].widget = forms.Select(attrs={'class': 'select2 form-select'})
            self.fields['hill'].label = mark_safe('Farmer | Hill')
            self.fields['hill'].queryset = daily_schedule.schedule.hills.order_by('farmer')
            self.fields['driver'].widget = forms.Select(attrs={'class': 'form-select'})
            self.fields['driver'].queryset = daily_schedule.schedule.drivers.order_by('name')
            self.fields['container_size'].label = mark_safe('m <sup>3</sup>')
            self.fields['container_size'].widget = forms.NumberInput(attrs={'class': 'form-control'})
            
    class Meta:
        model = Transportation
        fields = ['hill', 'driver', 'container_size']


############################################
# Manager Forms:

class YearForm(forms.Form):
    year = forms.TypedChoiceField(
        choices=[(str(year), str(year)) for year in range(2023, 2050)],
        coerce=int,
        empty_value=None,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg p-3'})
    )


class YearlyGasChargeForm(forms.Form):
    gas_charge = forms.FloatField(label=False, widget=forms.NumberInput(attrs={'class':'col form-control form-control-lg p-3'}))


class YearlyDistancePriceForm(forms.Form):
        distance = forms.IntegerField(label='Distance[km]', widget=forms.NumberInput(attrs={'class':'col form-control form-control-lg p-3'}))
        price = forms.FloatField(label='Price[CHF]', widget=forms.NumberInput(attrs={'class':'col form-control form-control-lg p-3'}))


class YearlyStationExportForm(forms.Form):
        station = forms.ModelChoiceField(queryset=Station.objects.all().order_by('station_name'), widget=forms.Select(attrs={'class': 'form-select form-select-lg p-3'}))
        export = forms.FloatField(label="Exported weight[t]",widget=forms.NumberInput(attrs={'class':'col form-control form-control-lg p-3'}))



class YearlyHillStationDistanceForm(forms.Form):
        hill = forms.ModelChoiceField(queryset=Hill.objects.all().order_by('farmer'), widget = forms.Select(attrs={'class': 'form-select form-select-lg p-3'}))
        distance = forms.FloatField(widget=forms.NumberInput(attrs={'class':'col form-control form-control-lg p-3'}))


# class ReceiptForm(forms.Form):
#     driver = forms.ModelChoiceField(queryset=Driver.objects.all().order_by('name'),
#                                     widget=forms.Select(
#                                          attrs={
#                                               'class':'col form-control form-control-lg p-3'}))

# class ReceiptForm(forms.Form):
#     driver = forms.ModelChoiceField(
#         queryset=Driver.objects.all().order_by('name'),
#         widget=forms.Select(
#             attrs={'class': 'selectpicker', 'data-live-search': 'true'}
#         )
#     )

class ReceiptForm(forms.Form):
    driver = forms.ModelChoiceField(
        queryset=Driver.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'select2 form-select p-3'})
    )

