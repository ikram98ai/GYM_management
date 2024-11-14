from django import forms
from .models import Member, HealthLog, Payment

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'birthdate', 'gender', 'contact_number', 'address', 'profile_photo']
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class HealthLogForm(forms.ModelForm):
    class Meta:
        model = HealthLog
        fields = ['weight', 'height']
        widgets = {
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }
    
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
