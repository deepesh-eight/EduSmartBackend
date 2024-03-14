from rest_framework import serializers

from constants import USER_TYPE_CHOICES
from . models import User, AddressDetails


class UserSignupSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )

    # address details
    address_line_1 = serializers.CharField(required=True)
    address_line_2 = serializers.CharField(required=False)
    city = serializers.CharField(required=True)
    state = serializers.CharField(required=False)
    country = serializers.CharField(required=True)
    pincode = serializers.CharField(required=True)


class AddressDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressDetails
        fields = [
            'address_line_1', 'address_line_2', 'city', 'state', 'country', 'pincode'
        ]


class UsersListSerializer(serializers.ModelSerializer):
    address_details = AddressDetailsSerializer(many=True)

    class Meta:
        model = User
        fields = ['user_type', 'name', 'email', 'phone', 'is_active', 'address_details']


class UpdateProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = [
            'name', 'email', 'phone',
        ]

    def update(self, instance, validated_data):
        if validated_data.get('name'):
            instance.name = validated_data.get('name')
        if validated_data.get('email'):
            instance.email = validated_data.get('email')
        if validated_data.get('phone'):
            instance.phone = validated_data.get('phone')
        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

