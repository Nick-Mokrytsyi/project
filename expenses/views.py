import json
from datetime import datetime

from django.db.models import Q
from django.shortcuts import render
from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get_queryset(self):

        queryset = super().get_queryset()

        sort_by = self.request.GET.get('sort_by')

        match sort_by:
            case "category":
                queryset = queryset.order_by('category__name')
            case "category_desc":
                queryset = queryset.order_by('-category__name')
            case "date":
                queryset = queryset.order_by('date')
            case 'date_desc':
                queryset = queryset.order_by('-date')

        category_ids = self.request.GET.getlist('category')

        if category_ids:
            queryset = queryset.filter(category__id__in=category_ids)
            # in: the field value is in a list of values;

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):

        queryset = object_list if object_list is not None else self.object_list

        form = ExpenseSearchForm(self.request.GET)

        if form.is_valid():
            name = form.cleaned_data.get('name', '').strip()
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            if name:
                queryset = queryset.filter(name__icontains=name)
                # icontains: the field value contains a given substring case-insensitive
            if from_date:
                from_datetime = datetime.combine(from_date, datetime.min.time())
                queryset = queryset.filter(date__gte=from_datetime)
                # gte: the field value is greater than or equal to a given value
            if to_date:
                to_datetime = datetime.combine(to_date, datetime.max.time())
                queryset = queryset.filter(date__lte=to_datetime)
                # lte: the field value is less than or equal to a given value;

        return super().get_context_data(
            form=form,
            object_list=queryset,
            summary_per_category=summary_per_category(queryset),
            **kwargs)


class CategoryListView(ListView):
    model = Category
    paginate_by = 5


def add_data_to_database(request):
    """The function give as the opportunity to open/read and sava data from .json to our database(sqlite)"""
    with open('fixtures.json', 'r') as file:
        data = json.load(file)

        for item in data:
            if item['model'] == 'expenses.category':
                category_fields = item['fields']
                Category.objects.update_or_create(pk=item['pk'], defaults=category_fields)
            elif item['model'] == 'expenses.expense':
                expense_fields = item['fields']
                category = Category.objects.get(pk=expense_fields['category'])
                expense_fields['category'] = category
                Expense.objects.update_or_create(pk=item['pk'], defaults=expense_fields)

    return render(request, 'base.html')


