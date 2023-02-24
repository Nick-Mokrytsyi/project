from django.urls import include, path
from django.views.generic.base import RedirectView
from expenses.views import add_data_to_database

urlpatterns = [
    path('',
         RedirectView.as_view(pattern_name='expenses:expense-list'),
         name='dashboard'),

    path('expenses/',
         include(('expenses.urls', 'expenses'), namespace='expenses')),

    path('add_data/', add_data_to_database, name='add_data'),
]
