from rest_framework import serializers

from accounts.models import CustomUser
from calculation.api.serializers import ExpensesSerializer
from group.api.serializers import GroupSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    # password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name']
        # fields = [ 'email', 'password', 'password2'] just to test form flutter
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
        try:
            password = self.validated_data['password']
            account = CustomUser(email=self.validated_data['email'], first_name=self.validated_data['first_name'],
                                 last_name=self.validated_data['last_name'])

            # account = User(email=self.validated_data['email'],
            account.set_password(password)
            account.save()
        except KeyError as error:
            raise serializers.ValidationError({'error': 'Please fill out all details'})
        return account


class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)
    # spender = ExpensesSerializer(many=True, read_only=True)
    member_of_group = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        exclude = ['password']
        # fields = ['email', 'expenses']

    def update(self, instance, validated_data):
        print('validated password data', validated_data)
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class SearchUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        exclude = ['password']

