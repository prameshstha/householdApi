from .views import RegistrationView, Login, Logout, UserListUpdateDelete, AllUsersList, VerificationView, \
    ResendActivationLink, SearchMembers
from django.contrib.auth import views as auth_views

from django.urls import path

urlpatterns = [
    path('login/', Login.as_view(), name='login-token'),  # post request only - login
    path('logout/', Logout.as_view(), name='logout-token'),  # post request only
    path('register/', RegistrationView.as_view(), name='register-token'),  # post request only
    path('user-list/', AllUsersList.as_view(), name='user-list'),  # get request only
    path('user-search/', SearchMembers.as_view(), name='user-search'),
    # patch and delete request only -(all edit of users and delete)
    path('user-edit-delete/<int:pk>/', UserListUpdateDelete.as_view(), name='user-edit-delete'),

    #     email activities
    path('activate/<uidb64>/<token>/', VerificationView.as_view(), name='activate'),
    path('resend_activation_link/', ResendActivationLink.as_view(), name='resend_activation_link'),

    #  for url launcher demo templates
    # path('recoverPassword/', RecoverPassword.as_view(), name='recover-password'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

]
