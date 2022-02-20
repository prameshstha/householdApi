from rest_framework import serializers

from calculation.api.serializers import ExpensesSerializer, FinalTransactionSerializer, PersonalTotalSerializer, CalculationPeriodSerializer
from calculation.models import CalculationPeriod
from group.models import Groups


class GroupSerializer(serializers.ModelSerializer):
    exp_of_group = ExpensesSerializer(many=True, read_only=True)
    group_final_transaction = FinalTransactionSerializer(many=True, read_only=True)
    group_personal_total = PersonalTotalSerializer(many=True, read_only=True)
    # calculation_cycle_group = CalculationPeriodSerializer(many=True, read_only=True)
    calculation_cycle = serializers.SerializerMethodField()

    class Meta:
        model = Groups
        fields = '__all__'

    def get_calculation_cycle(self, instance):
        print('qxxxxxx', instance)
        try:
            qs = CalculationPeriod.objects.get(is_active=True, group_id=instance.id)
            print('qsssssssssssssssss', qs)
            return CalculationPeriodSerializer(qs, read_only=True).data
        except CalculationPeriod.DoesNotExist:
            return None

