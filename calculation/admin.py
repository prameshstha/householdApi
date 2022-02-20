from django.contrib import admin

# Register your models here.
from calculation.models import CalculationPeriod, Expenses, FinalTransaction, TotalExpenses, PersonalTotal

admin.site.register(CalculationPeriod)
admin.site.register(Expenses)
admin.site.register(FinalTransaction)
admin.site.register(TotalExpenses)
admin.site.register(PersonalTotal)