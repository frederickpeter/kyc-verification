from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("phone_number", "password", "full_name", "document")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data["password"]
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.is_active = True
        instance.save()

        return instance

    def validate(self, attrs):
        if User.objects.filter(phone_number__exact=attrs["phone_number"]).exists():
            raise serializers.ValidationError("Phone number already exists")
        return super().validate(attrs)
