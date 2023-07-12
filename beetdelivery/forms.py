from django import forms
from .models import Farmer, Driver, Station, Schedule, Transportation, YearlyStationExport, YearlyHillStationDistance, YearlyGasCharge, YearlyDistancePrice, Hill
import datetime
from django.utils.safestring import mark_safe

class DateStationForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class':'col form-control form-control-lg p-3'}))
    station = forms.ModelChoiceField(queryset=Station.objects.all(), widget=forms.Select(attrs={'class':'col form-control form-control-lg p-3'}))

class TransportationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        daily_schedule = kwargs.pop('daily_schedule', None)
        super(TransportationForm, self).__init__(*args, **kwargs)
        if daily_schedule:
            self.instance.daily_schedule = daily_schedule
            self.fields['hill'].widget = forms.Select(attrs={'class': 'form-select form-select-lg p-3'})
            self.fields['hill'].label = mark_safe('Farmer&Hill')
            self.fields['hill'].queryset = daily_schedule.schedule.hills
            self.fields['driver'].widget = forms.Select(attrs={'class': 'form-select form-select-lg p-3'})
            self.fields['driver'].queryset = daily_schedule.schedule.drivers
            self.fields['container_size'].label = mark_safe('m <sup>3</sup>')
            self.fields['container_size'].widget = forms.NumberInput(attrs={'class': 'form-control form-control-lg p-3'})
            
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
    gas_charge = forms.FloatField(widget=forms.NumberInput(attrs={'class':'col form-control form-control-lg p-3'}))


class YearlyDistancePriceForm(forms.Form):
        distance = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'col form-control form-control-lg p-3'}))
        price = forms.FloatField(widget=forms.NumberInput(attrs={'class':'col form-control form-control-lg p-3'}))


class YearlyStationExportForm(forms.Form):
        station = forms.ModelChoiceField(queryset=Station.objects.all(), widget=forms.Select(attrs={'class': 'form-select form-select-lg p-3'}))
        # station = forms.ModelChoiceField(queryset=Station.objects.all(), widget=forms.Select(attrs={'class':'col form-control form-control-lg p-3'}))

        export = forms.FloatField(widget=forms.NumberInput(attrs={'class':'col form-control form-control-lg p-3'}))
        # density = forms.FloatField()


class YearlyHillStationDistanceForm(forms.Form):
        hill = forms.ModelChoiceField(queryset=Hill.objects.all(), widget = forms.Select(attrs={'class': 'form-select form-select-lg p-3'}))
        distance = forms.FloatField(widget=forms.NumberInput(attrs={'class':'col form-control form-control-lg p-3'}))


class ReceiptForm(forms.Form):
    driver = forms.ModelChoiceField(queryset=Driver.objects.all(),widget=forms.Select(attrs={'class':'col form-control form-control-lg p-3'}))
    # year = forms.TypedChoiceField(
    #     choices=[(str(year), str(year)) for year in range(2023, 2050)],
    #     coerce=int,
    #     empty_value=None,
    #     widget=forms.Select(attrs={'class':'col form-control form-control-lg'})
    # )
