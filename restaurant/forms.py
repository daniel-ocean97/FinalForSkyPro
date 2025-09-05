from django import forms
from .models import Reservation, Table

class ReservationStep1Form(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'reservationDate'
        })
    )
    time = forms.TimeField(widget=forms.HiddenInput())
    guests_count = forms.ChoiceField(
        choices=[(i, f"{i} человек") for i in range(1, 21)],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'guestsCount'})
    )

class ReservationStep2Form(forms.Form):
    table = forms.ModelChoiceField(
        queryset=Table.objects.none(),
        widget=forms.HiddenInput()
    )

class ReservationStep3Form(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['client_name', 'client_phone', 'client_email', 'special_requests']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'clientName'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-control', 'id': 'clientPhone'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'clientEmail'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'id': 'specialRequests', 'rows': 3}),
        }