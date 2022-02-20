from rest_framework.permissions import IsAuthenticated

from calculation.models import CalculationPeriod, Expenses, FinalTransaction
from group.api.serializers import GroupSerializer
from group.models import Groups
from rest_framework import parsers, renderers, generics, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import CustomUser


class AllGroupList(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = Groups.objects.all()
    serializer_class = GroupSerializer


class GroupUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = Groups.objects.all()
    serializer_class = GroupSerializer


def getGroupById(group_id):
    final_group = {}

    group_members = []
    memberInGroup = Groups.objects.get(id=group_id)
    for m in memberInGroup.group_members.all():
        group_member = {}
        print(m.id)
        group_member['id'] = m.id
        group_member['first_name'] = m.first_name
        group_member['last_name'] = m.last_name
        group_member['user_image'] = str(m.user_image)

        group_members.append(group_member)

    final_group['id'] = memberInGroup.id
    final_group['group_admin'] = memberInGroup.group_admin.id
    final_group['group_pic'] = str(memberInGroup.group_pic)
    final_group['group_name'] = memberInGroup.group_name
    final_group['group_members'] = group_members
    print(final_group)
    return final_group


class AddGroupMember(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        print(request.data, kwargs)
        new_member = request.data['new_member']
        group_id = request.data['group_id']
        group = Groups.objects.get(id=group_id)
        data = {}

        try:
            member = CustomUser.objects.get(id=new_member)
            try:
                memberInGroup = Groups.objects.get(group_members=member, id=group_id)
                data['result'] = 'This member already exists this group.'
                return Response(data, 409)

            except Groups.DoesNotExist:
                add_in_group = group.group_members.add(member)
                try:

                    # domain = get_current_site(request).domain
                    # dashboard_link = 'http://' + domain + '/dashboard/'
                    # context = {
                    #     'memberAdded': 'New member added in the group ' + group.group_name + '.',
                    #     'memberIngroup': memberInGroup,
                    #     'group': memberInGroup,
                    #     'user': request.user.first_name + ' ' + request.user.last_name,
                    #     'dashboard_link': dashboard_link,
                    #     'userEmail': request.user.email,
                    # }
                    #
                    # #     send email to new member
                    # email_subject = request.user.username + ' added you to group ' + "'" + str(group) + "'"
                    # html_message = render_to_string('email/addMember.html', context)
                    # plain_message = strip_tags(html_message)
                    # from_email = settings.EMAIL_HOST_USER
                    # to_email = [NewEmail]
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
                    final_group = getGroupById(member, group_id)
                    return Response(final_group, 200)

                except Groups.DoesNotExist:
                    data['result'] = 'Member not added.'
                    return Response(data)
        except CustomUser.DoesNotExist:
            data['result'] = 'This email address does not have account in this app. Do you want to invite them?'
            return Response(data, 404)
        except CustomUser.MultipleObjectsReturned:
            data['result'] = 'Something is wrong. Please try again.'
            return Response(data, 404)


class RemoveMember(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = {}
        print(request.data)
        member_id = request.data['member_id']
        group_id = request.data['group_id']
        group = Groups.objects.get(id=group_id)
        try:
            cal_period = CalculationPeriod.objects.get(group_id=group_id, is_active=True)
            print(cal_period)
            data['result'] = 'Deletion failed. Calculation period is still active. Settle calculation and try again. '
            return Response(data, 404)
        except CalculationPeriod.DoesNotExist:
            print(group.group_admin.id, member_id, 'idddddddddddddd')
            print(int(group.group_admin.id) == int(member_id))
            if int(group.group_admin.id) == int(member_id):
                data['result'] = 'Please change admin before removing admin member'
                return Response(data, 409)
            group.group_members.remove(member_id)
            final_group = getGroupById(group_id)
            return Response(final_group, 200)


class ChangeAdmin(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = {}
        print(request.data)
        group_id = request.data['group_id']
        member_id = request.data['member_id']
        admin_id = request.data['admin_id']
        try:
            member = CustomUser.objects.get(id=member_id)
            group_instance = Groups.objects.get(id=group_id)
            print(member, group_instance, '-==-=================')
            if int(group_instance.group_admin.id) == int(admin_id):
                group_instance.group_admin = member
                group_instance.save()
                final_group = getGroupById(group_id)
                return Response(final_group, 200)
            else:
                data['result'] = 'Unauthorized process for normal user.'
                return Response(data, 404)
        except Exception as e:
            print(e)
            data['result'] = str(e)
            return Response(data, 404)

        # #     send email to new member
        # domain = get_current_site(request).domain
        # dashboard_link = 'http://' + domain + '/dashboard/'
        # email_subject = request.user.first_name + ' has added you as group admin of ' + "'" + str(group_instance) + "'"
        # email_body = request.user.first_name + ' has added you as group admin of ' + "'" + str(
        #     group_instance) + "'.\n" + 'Visit link below to access website\n' + dashboard_link
        # from_email = settings.EMAIL_HOST_USER
        # to_email = [member.email]
        #
        # send_email = EmailMultiAlternatives(
        #     email_subject,
        #     email_body,
        #     from_email,
        #     to_email,
        #
        # )
        # EmailThread(send_email).start()


class GetGroupDetails(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):

        group_id = request.data['group_id']
        user_id = request.data['user_id']
        print('get members', request.data)
        # seleected_group = Groups.objects.get(id=group_id)
        data = {}
        group_instance = Groups.objects.get(id=group_id)
        logged_user = CustomUser.objects.get(id=user_id)
        # memberIngroup = Groups.objects.get(id=group_id)
        try:
            cal_period = CalculationPeriod.objects.get(group_id=group_id, is_active=True)
            # need to edit
            # created_cal_period_json = serializers.serialize("json", cal_period)
            print('cal period', cal_period)
            g_expenses = Expenses.objects.filter(group_id=group_id, calculation_period=cal_period).order_by('-added')
            if g_expenses:
                group_expenses = g_expenses
            else:
                group_expenses = ''
            final_transaction = FinalTransaction.objects.filter(group_id=group_id, calculation_period=cal_period).order_by(
                '-id')

            print(group_id, final_transaction)
            # toUser = FinalTransaction.objects.filter(group_id=group_id, calculation_period=calculation_period).aggregate(
            #     totalExpenses=Sum('total_amount'))
            print('final transation')
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
            context = {
                'memberAdded': 'New member added in the group ' + 'group_name' + '.',
                'memberIngroup': group_instance,
                'group_expenses': group_expenses,
                'final_transaction': final_transaction,
                'owe': owe,
                'owned': owned,
                'total_balance': total_balance,
                'cal_period': cal_period,
                'ActiveCalculationPeriod': 'Calculation period is active from: ' + str(cal_period.start_period) + '.'
            }
            return Response(data, 200)
        except CalculationPeriod.DoesNotExist:
            context = {
                'ActiveCalculationPeriod': 'No active calculation period for this group.',
                # 'memberIngroup': group_instance,
                'owe': 0,
                'owned': 0,
                'total_balance': 0,
                'final_transaction': ''
            }
            print(context)
            return Response(context, 200)


class AddFriendMember(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):

        print('addedFriendMessage')
        print(request.data)
        group_id = request.data['group_id']
        friend_id = request.data['friend_id']
        try:
            get_group = Groups.objects.get(id=group_id, group_members=friend_id)
            context = {
                'result': 'This user is already in this group.'
            }
            return Response(context, 409)
        except Groups.DoesNotExist:
            try:
                group = Groups.objects.get(id=group_id)
                group.group_members.add(friend_id)

                context = {
                    'result': 'New member added in the group.'
                }
                return Response(context, 200)
            except Groups.DoesNotExist:
                context = {
                    'result': 'No such group in records.'
                }
                return Response(context, 404)