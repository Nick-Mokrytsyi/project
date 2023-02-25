import json
from datetime import datetime

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
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

        total_amount = queryset.aggregate(total=Sum('amount'))['total']
        """
        In Django, the aggregate method is a queryset method that allows you to compute an aggregate value over 
        the queryset, such as the sum, average, minimum, or maximum value of a specific field. The aggregate method 
        takes one or more keyword arguments that specify the aggregation functions to apply, and the fields to which 
        those functions should be applied. Each keyword argument should be in the form <name>=<function>('field'), 
        where <name> is a name for the result of the aggregation, <function>(import from Django db.models  is the 
        aggregation function to apply, and 'field' is the name of the field to which the aggregation 
        function should be applied. 
        """

        summary_per_month = queryset.annotate(year_month=TruncMonth('date')).values('year_month').annotate(
            total=Sum('amount')).order_by('-year_month')

        """
        Not mine method, GOOGLE/STACKOVERFLOW help me to do it, a little bit hard to understand it

        n Django, annotate is a queryset method that allows you to add computed fields to each object in the queryset 
        based on the values of one or more fields. These computed fields can be used for filtering, ordering, 
        or displaying the data in the template. The annotate method takes one or more keyword arguments that specify 
        the computed fields to add, and the functions or expressions used to compute their values. Each keyword 
        argument should be in the form <name>=<expression>, where <name> is the name of the computed field, 
        and <expression> is the function or expression used to compute its value. 

        """

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
            total_amount=round(total_amount, 2),
            summary_per_category=summary_per_category(queryset),
            summary_per_month=summary_per_month,
            **kwargs)


class CategoryListView(ListView):
    model = Category
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(expense_count=Count('expense'))
        return queryset


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


# class CategoryUpdateView(UpdateView):
#     model = Category
#     template_name = 'category_update.html'
#     form_class = CategoryUpdateForm
#     success_url = reverse_lazy('expenses:expense-list')
