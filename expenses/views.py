import json

from django.shortcuts import render
from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list

        form = ExpenseSearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get('name', '').strip()
            if name:
                queryset = queryset.filter(name__icontains=name)

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
