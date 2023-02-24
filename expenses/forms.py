from django import forms
from django.db.models import Q
from django.shortcuts import render

from .models import Expense


class ExpenseSearchForm(forms.ModelForm):
    from_date = forms.DateField(label='from', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(label='to', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Expense
        fields = ('name', 'from_date', 'to_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
