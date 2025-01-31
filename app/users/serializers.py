from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from app.users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('user', 'id',)

class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=get_user_model().objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    profile = ProfileSerializer(required=False)

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number', 'is_guest', 'profile',)
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': False},
            'is_guest': {'required': False},
        }

    def validate(self, attrs):
        is_exists = get_user_model().objects.filter(email=attrs.get('email')).exists()
        if is_exists:
            raise serializers.ValidationError({'email': 'Email already exists'})
        return attrs

    def create(self, validated_data):
        user = get_user_model().objects.create(
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            phone_number=validated_data.get('phone_number', ''),
            is_guest=validated_data.get('is_guest', False)
        )
        
        user.set_password(validated_data.get('password'))
        user.save()
        profile_data = validated_data.get('profile', {})
        if profile_data:
            Profile.objects.create(user=user, **profile_data)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(CustomTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['username'] = user.username
        return token


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'first_name',
            'last_name',
            'is_guest',
            'profile',
        )

    def get_profile(self, obj):
        profile = Profile.objects.filter(user=obj).first()
        if profile is None:
            return {}
        return ProfileSerializer(profile).data


