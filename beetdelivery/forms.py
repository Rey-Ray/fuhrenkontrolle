from django import forms
from .models import Farmer, Driver, Station, Schedule, Transportation, YearlyStationExport, YearlyHillStationDistance
import datetime

class DateStationForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    station = forms.ModelChoiceField(queryset=Station.objects.all())

class TransportationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        daily_schedule = kwargs.pop('daily_schedule', None)
        super(TransportationForm, self).__init__(*args, **kwargs)
        if daily_schedule:
            self.instance.daily_schedule = daily_schedule
            self.fields['hill'].queryset = daily_schedule.schedule.hills
            self.fields['driver'].queryset = daily_schedule.schedule.drivers

    class Meta:
        model = Transportation
        fields = ['hill', 'driver', 'container_size']

class ScheduleForm(forms.Form):
    hill = forms.ModelChoiceField(queryset=Farmer.objects.all(), label='Select Hill')
    driver = forms.ModelChoiceField(queryset=Driver.objects.all(), label='Select Driver')
    quantity = forms.IntegerField()
    
    def __init__(self, date=None, station=None, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        if date and station:
            schedule = Schedule.objects.get(date=date, station=station)
            self.fields['hill'].queryset = schedule.hills
            self.fields['driver'].queryset = schedule.drivers

class YearForm(forms.Form):
    year = forms.TypedChoiceField(
        choices=[(str(year), str(year)) for year in range(2023, 2050)],  # Example: range from 2000 to 2050
        coerce=int,
        empty_value=None,
        widget=forms.Select
    )
    gas_charge = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'small-input'}))
    def clean_gas_charge(self):
        gas_charge = self.cleaned_data.get('gas_charge')
        if gas_charge < -99 or gas_charge > 99:
            raise forms.ValidationError("gas_charge must be between -99 and 99.")
        return gas_charge

    # class Meta:
    #     model = Year
    #     fields = ['year', 'gas_charge']
    # #year = forms.ChoiceField()
    # #gas_charge = forms.FloatField()

class YearlyDistancePriceForm(forms.Form):
    for i in range(1, 71):
        locals()['distance_' + str(i)] = forms.CharField(label=str(i), max_length=100)

class YearlyStationExportForm(forms.ModelForm):
    class Meta:
        model = YearlyStationExport
        fields = ['total_tons', 'density', 'station']
        # widgets = {
        #     'total_tons': forms.NumberInput(attrs={'class': 'small-input'}),
        #     'density': forms.NumberInput(attrs={'class': 'small-input'}),
        #     # 'station': forms.Textarea()
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['station'].disabled = True

YearlyStationExportFormset = forms.modelformset_factory(YearlyStationExport, form=YearlyStationExportForm, extra=0)

class YearlyHillStationDistanceForm(forms.ModelForm):
    class Meta:
        model = YearlyHillStationDistance
        fields = ['hill', 'distance']
        # widgets = {
        #     'total_tons': forms.NumberInput(attrs={'class': 'small-input'}),
        #     'density': forms.NumberInput(attrs={'class': 'small-input'}),
        #     # 'station': forms.Textarea()
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hill'].disabled = True

YearlyHillStationDistanceFormset = forms.modelformset_factory(YearlyHillStationDistance, form=YearlyHillStationDistanceForm, extra=0)
