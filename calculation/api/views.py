from datetime import datetime
from decimal import Decimal

from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CustomUser
from calculation.api.serializers import ExpensesSerializer, FinalTransactionSerializer, CalculationPeriodSerializer
from calculation.models import CalculationPeriod, PersonalTotal, FinalTransaction, Expenses, final_calculation
from group.api.serializers import GroupSerializer
from group.api.views import getGroupById
from group.models import Groups
from rest_framework import generics


class CreateCalculationCycle(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = {}
        print(request.data)
        group_id = request.data['group_id']
        group_instance = Groups.objects.get(id=group_id)
        try:
            old_calculation_period = CalculationPeriod.objects.get(group_id=group_instance, is_active=True)
            final_group = getGroupById(group_id)
            context = {

                'result': 'Calculation period already active from: ' + str(
                    old_calculation_period.start_period) + '.', }
            return Response(context, 409)

        except CalculationPeriod.DoesNotExist:
            new_calculation_period = CalculationPeriod.objects.create(group_id=group_instance, is_active=True)
            if new_calculation_period:
                print('calculation')
                for x in group_instance.group_members.all():
                    print(x)
                    PersonalTotal.objects.create(group_id=group_instance, total_amount=0, spender_id=x,
                                                 calculation_period=new_calculation_period)
                # domain = get_current_site(request).domain
                # dashboard_link = 'http://' + domain + '/dashboard/'
                final_group = getGroupById(group_id)
                context = {
                    'ActiveCalculationPeriod': 'Calculation period is active from: ' + str(
                        new_calculation_period.start_period) + '.',
                    'group_details': final_group,
                    # 'cal_period': new_calculation_period.,
                    'owe': 0,
                    'owned': 0,
                    'total_balance': 0,
                    'message': 'New Calculation cycle is created. Now you CANNOT add or remove members form this group.',
                    # context for email
                    'group_name_for_email': group_instance.group_name,
                    # 'dashboard_link': dashboard_link,
                    # 'userEmail': request.user.email,
                    # 'user': request.user.first_name + ' ' + request.user.last_name,
                    'start_period': new_calculation_period.start_period,
                }
                # send email creating new calculation cycle.

                # membersEmail = group_instance.group_members.all()
                # memEmail = []
                # for me in membersEmail:
                #     if me.email != request.user.email:
                #         memEmail.append(me.email)
                #
                # email_subject = request.user.username + ' created new cycle ' + ' of the group ' + "'" + str(
                #     group_instance) + "'"
                # html_message = render_to_string('email/startCycle.html', context)
                # plain_message = strip_tags(html_message)
                # from_email = settings.EMAIL_HOST_USER
                # to_email = memEmail
                #
                # email_body = plain_message
                #
                # send_email = EmailMultiAlternatives(
                #     email_subject,
                #     email_body,
                #     from_email,
                #     to_email,
                #
                # )
                # send_email.attach_alternative(html_message, "text/html")
                # EmailThread(send_email).start()
        print(context)
        return Response(context, 200)


class AddExpenses(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)
        group_id = request.data['group_id']
        user_id = request.data['spender']
        # exp_note = request.data['exp_note']
        amt = request.data['amount']
        logged_user = CustomUser.objects.get(id=user_id)
        # try:
        #     bill = request.data['bill']
        # except MultiValueDictKeyError:
        #     context = {
        #         'result': 'Bill attachment required.'
        #     }
        #     return Response(context, 409)
        #
        try:
            amount = Decimal(amt)
        except amt.InvalidOperation:
            context = {'result': 'Value conversion error.'}
            return Response(context, 409)
        print(amount, 'amount')
        try:
            group_instance = Groups.objects.get(id=group_id)
            cal_period = CalculationPeriod.objects.get(group_id=group_instance, is_active=True)
            expense_serializer = ExpensesSerializer(data=request.data)
            if expense_serializer.is_valid():
                expense_saved = expense_serializer.save()
                print(expense_saved.calculation_period)
                expense_saved.calculation_period = cal_period
                print(expense_saved.calculation_period)
                expense_saved.save()
                if expense_saved:
                    group_expenses = Expenses.objects.filter(group_id=group_id, calculation_period=cal_period).order_by(
                        '-id')
                    print('group expetdsssssssssssss', group_expenses)
                    try:
                        print('bbbbbbbbbbbbbbbbb')
                        personal_t = PersonalTotal.objects.get(group_id=group_id, spender_id=user_id,
                                                               calculation_period=cal_period)
                        print(personal_t.total_amount)
                        peronal_total = personal_t.total_amount + amount
                        print(peronal_total)
                        personal_t.total_amount = peronal_total
                        a = personal_t.save()
                        print(a, 'bbcc')
                        print('cccccccccccccccccccccccc')
                        final_calculation(group_id)
                        final_transaction = FinalTransaction.objects.filter(group_id=group_id,
                                                                            calculation_period=cal_period)
                        owe = 0
                        owned = 0
                        for u in final_transaction:
                            print(u.to_user)
                            if u.to_user == logged_user:
                                owned += u.amount
                            if u.from_user == logged_user:
                                owe += u.amount

                        print('ffffffffffffffffff', owe, owned)
                        total_balance = owned - owe
                        # total_exp(group_id)
                        print('eeeeeeeeeeeeeeeeee')
                        final_transaction_serializer = FinalTransactionSerializer(final_transaction, many=True)
                        g_ser = GroupSerializer(group_instance)
                        exp_ser = ExpensesSerializer(group_expenses, many=True)
                        context = {
                            'memberAdded': 'Expenses added ' + 'group_name' + '.',
                            'expAdded': 'Added',
                            'group_expenses': exp_ser.data,
                            'final_transaction': final_transaction_serializer.data,
                            'owe': owe,
                            'owned': owned,
                            'total_balance': total_balance,
                            'group': g_ser.data,
                            'amount': amount,
                        }
                        return Response(context, 200)

                    except PersonalTotal.DoesNotExist:
                        print('dddddddddddddddddddd')
                        PersonalTotal.objects.create(group_id=group_instance, total_amount=amount,
                                                     spender_id=logged_user,
                                                     calculation_period=cal_period)
                        context = {'result': 'Something went wrong.'}
                        return Response(context, 404)

            else:
                expense_serializer.errors['status'] = False
                context = {
                    'result': expense_serializer.errors
                }
                return Response(context, 409)

        except Exception as error:
            context = {'result': str(error)}
            return Response(context, 404)


class SettleCalculationCycle(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = {}
        group_id = request.POST['group_id']
        group_instance = Groups.objects.get(id=group_id)
        try:
            old_calculation_period = CalculationPeriod.objects.get(group_id=group_instance, is_active=True)
            old_calculation_period.is_active = False
            old_calculation_period.end_period = datetime.now()
            old_calculation_period.save()
            print(old_calculation_period.is_active)
            is_active = old_calculation_period.is_active
            if not is_active:
                # domain = get_current_site(request).domain
                # dashboard_link = 'http://' + domain + '/dashboard/'
                final_transaction = FinalTransaction.objects.filter(calculation_period=old_calculation_period)
                print(final_transaction)
                final_transaction_serializer = FinalTransactionSerializer(final_transaction, many=True)
                print('----------------------------------------------------')
                final_group = getGroupById(group_id)
                context = {
                    'ActiveCalculationPeriod': 'No active calculation period for this group.',
                    'group': final_group,
                    'message': 'Settled period cycle. Please refer to Final Calculation tab for calculations.',
                    # context for email
                    # 'group': group_instance,
                    # 'dashboard_link': dashboard_link,
                    # 'userEmail': request.user.email,
                    # 'user': request.user.first_name + ' ' + request.user.last_name,
                    'start_period': old_calculation_period.start_period,
                    'end_period': old_calculation_period.end_period,
                    'final_transaction_email': final_transaction_serializer.data,
                }
                # send email after settling calculation cycle.

                # membersEmail = group_instance.group_members.all()
                # memEmail = []
                # for me in membersEmail:
                #     if me.email != request.user.email:
                #         memEmail.append(me.email)
                #
                # email_subject = request.user.username + ' settled old cycle ' + ' of the group ' + "'" + str(
                #     group_instance) + "'"
                # html_message = render_to_string('email/settleCycle.html', context)
                # plain_message = strip_tags(html_message)
                # from_email = settings.EMAIL_HOST_USER
                # to_email = memEmail
                #
                # email_body = plain_message
                #
                # send_email = EmailMultiAlternatives(
                #     email_subject,
                #     email_body,
                #     from_email,
                #     to_email,
                #
                # )
                # send_email.attach_alternative(html_message, "text/html")
                # EmailThread(send_email).start()
                return Response(context, 200)

        except CalculationPeriod.DoesNotExist:
            data['result'] = 'No Calculation Cycle to settle'
            return Response(data, 404)


class ShowPastTransactions(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data['user_id']
        user = CustomUser.objects.get(id=user_id)
        try:
            selected_groups = Groups.objects.filter(group_members=user)
            cal_period = CalculationPeriod.objects.filter(group_id__in=selected_groups, is_active=False)
            print('seeeeeeeeleeleelellele', selected_groups, cal_period)
            # calculate total balance
            past_final_trans = FinalTransaction.objects.filter(calculation_period__in=cal_period)
            final_transaction_serializer = FinalTransactionSerializer(past_final_trans, many=True)
            # group_serializer = GroupSerializer(selected_groups, many=True)
            # cal_serializer = CalculationPeriodSerializer(cal_period, many=True)

            context = {
                'past_final_trans': final_transaction_serializer.data,
                # 'selected_groups': group_serializer.data,
                # 'cal_period': cal_serializer.data,
            }
            return Response(context, 200)
        except Exception as e:
            context = {'result': str(e)}
            return Response(context, 404)


class FinalTransactionSort(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ft_id = request.data['final_trans_id']
        print(ft_id)
        ft = FinalTransaction.objects.get(id=ft_id)
        ft.is_paid = True
        ft.save()
        print(ft)
        context = {'result': 'Success'}
        return Response(context, 200)


# def final_transaction_email(request):
#     template = 'groups/dashboard.html'
#     context = {}
#     if request.POST:
#         ft_id = request.POST['id']
#         print(ft_id)
#         ft = FinalTransaction.objects.get(id=ft_id)
#         toemail = ft.from_user
#         print(toemail)
#         print(ft.from_user.first_name)
#
#         # send email for payment notice.
#         email_subject = request.user.first_name + ' has requested for payment.'
#         from_email = settings.EMAIL_HOST_USER
#         to_email = [toemail]
#
#         email_body = 'Hi ' + ft.from_user.first_name + '\n' + request.user.first_name + '(' + request.user.email + ') has requested for the payment of ' \
#                                                                           'amount $' + str(ft.amount) + ' from your group ' + "'" +str(ft.group_id) + "'" + '.\n'
#         send_email = EmailMultiAlternatives(
#             email_subject,
#             email_body,
#             from_email,
#             to_email,
#
#         )
#         EmailThread(send_email).start()
#
#     if request.is_ajax():
#         html = render_to_string(template, context, request=request)
#     return JsonResponse({'post': html})
