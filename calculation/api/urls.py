from .views import CreateCalculationCycle, SettleCalculationCycle, AddExpenses, ShowPastTransactions

from django.urls import path

urlpatterns = [
    path('create-cycle/', CreateCalculationCycle.as_view(), name='create-cycle'),
    path('settle-cycle/', SettleCalculationCycle.as_view(), name='settle-cycle'),
    path('add-expenses/', AddExpenses.as_view(), name='add-expenses'),
    path('past-transaction/', ShowPastTransactions.as_view(), name='past-transaction'),

]
