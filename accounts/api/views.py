
import threading

from django.conf import settings
from django.contrib.auth import logout, authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.forms import model_to_dict
from django.shortcuts import render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.permissions import IsAuthenticated
from accounts.codeGenerator import token_generator
from .serializers import RegistrationSerializer, SearchUserSerializer
from rest_framework import parsers, renderers, generics, serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from accounts.models import CustomUser


class RegistrationView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        print(request.data)
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            print('valid')
            user = serializer.save()
            token = Token.objects.create(user=user)
            data['email'] = user.email
            data['first_name'] = user.first_name
            data['last_name'] = user.last_name
            data['is_active'] = user.is_active
            data['is_staff'] = user.is_staff
            data['is_superuser'] = user.is_superuser
            data['user_phone'] = user.user_phone
            data['token'] = token.key
            data['user_id'] = user.id

            return Response(data, 200)
        else:
            data = serializer.errors
            # print(data)
            # a = json.dumps(data.get('email'))
            # print(list(data))
            # if a==["CustomUser with this email already exists."]:
            #     print('sy')

        return Response(data, 403)


class Login(APIView):

    def post(self, request):
        print(request.data)
        email = request.data['email']
        password = request.data['password']

        if email and password:
            try:
                # Try to find a user matching your username
                user = CustomUser.objects.get(email=email)
                pwd_valid = check_password(password, user.password)
                print(pwd_valid)
                #  Check the password is the reverse of the username
                # something wrong here need to check asap
                if pwd_valid:
                    # Yes? return the Django user object
                    token = Token.objects.get_or_create(user=user)
                    # user_dict = (model_to_dict(user))
                    # user_dict.pop('last_login')
                    # user_dict.pop('date_joined')
                    # user_dict.pop('groups')
                    # user_dict.pop('user_permissions')
                    # user_dict.pop('password')
                    # print(token[0])
                    us = UserSerializer(user)
                    context = {'token': str(token[0]), 'user': us.data}
                    # user_dict['token'] = str(token[0])
                    return Response(context, 200)
                else:
                    # No? return None - triggers default login failed
                    return Response({'Error': 'Email or Password wrong'}, 403)
            except CustomUser.DoesNotExist:
                # No user was found, return None - triggers default login failed
                return Response({'Error': 'User Does not exist'}, 404)


class Logout(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print(request.user)
        print(request.data)
        logout(request)
        return Response({'message': 'User Logged out'})


class UserListUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class AllUsersList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class SearchMembers(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print(request.data)
        search_txt = request.data['search_text']
        print(search_txt)
        search_user = CustomUser.objects.filter(email__icontains=search_txt)
        print(search_user)
        search_user_serializer = SearchUserSerializer(search_user, many=True)

        context = {'searchUser': search_user_serializer.data}
        return Response(context, 200)



# email activities below
# to send email faster
class EmailThread(threading.Thread):
    def __init__(self, send_email):
        self.send_email = send_email
        threading.Thread.__init__(self)

    def run(self):
        self.send_email.send(fail_silently=False)


def send_activation_email(request, toemail):
    email_subject = 'Activate your account'
    user = CustomUser.objects.get(email=toemail)
    # path_to_view
    # - getting domain we are on
    # - relative url to verification
    # - encode uid
    # - token

    uidb64 = urlsafe_base64_encode(force_bytes(user))
    domain = get_current_site(request).domain
    link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
    activate_url = 'http://' + domain + link

    email_body = 'Hi ' + str(user.first_name) + ', ' + 'Use the below link to activate you account \n' + activate_url
    from_email = settings.EMAIL_HOST_USER
    to_email = [toemail]
    send_email = EmailMultiAlternatives(
        email_subject,
        email_body,
        from_email,
        to_email,
    )
    EmailThread(send_email).start()


class VerificationView(APIView):
    def get(self, request, uidb64, token):
        context = {}
        statusCode = 409
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(email=uid)
            print(user.is_active, 'is active', user)

        except Exception as identifier:
            user = None
            context = {
                'activationMessage': 'Something went wrong. Please re request the activation link below.',
                'success': 'fail',
            }

        if user is not None and token_generator.check_token(user, token):
            print(user.is_active)
            if user.is_active:
                print('sssssssssssssssssssss')
                context = {
                    'activationMessage': 'Account already activated. Login to get access.',
                    'success': 'success',
                }

            else:
                user.is_active = True
                user.save()
                print('ttttttttttttttttttttttt')
                context = {
                    'activationMessage': 'Account activation successful.',
                    'success': 'success',
                }
                statusCode = 200

        else:
            context = {
                'activationMessage': 'The activation link is expired or broken. ',
                'success': 'fail',
            }
        return render(request, 'registration/activationMessage.html', context)

        # return Response(context, statusCode)


class ResendActivationLink(APIView):
    def post(self, request):
        print(self.request.data)
        context = {}
        email = self.request.data['email']
        try:
            user = CustomUser.objects.get(email=email)
            print(user)
            if user:
                send_activation_email(request, email)
                context = {
                    'message': 'Activation Link sent. Please check your email and activate.'
                }
        except CustomUser.DoesNotExist:
            print('not exist')

            context = {
                'message': 'This account is not in the system. Please register.',

            }

        return Response(context, 200)
