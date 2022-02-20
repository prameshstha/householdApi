from rest_framework import serializers

# from accounts.api.serializers import UserSerializer
from accounts.models import CustomUser
from calculation.models import Expenses, FinalTransaction, PersonalTotal, CalculationPeriod


class ExpensesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expenses
        fields = '__all__'


class FinalTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = FinalTransaction
        fields = '__all__'


class PersonalTotalSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalTotal
        fields = '__all__'


class CalculationPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = CalculationPeriod
        fields = '__all__'




