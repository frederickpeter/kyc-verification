from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    document = serializers.FileField(required=True)

    class Meta:
        model = User
        fields = ("phone_number", "password", "full_name", "document", "email")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data["password"]
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.is_active = True
        instance.save()

        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "phone_number",
            "email",
            "is_kyc_verified",
            "kyc_rejection_reason",
            "profile_photo",
            "document",
        )


class ApproveKYCSerializer(serializers.Serializer):
    def save(self, user):
        user.is_kyc_verified = True
        user.kyc_rejection_reason = ""
        user.save()


class RejectKYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("kyc_rejection_reason",)
        extra_kwargs = {
            "kyc_rejection_reason": {"required": True},
        }

    def save(self, instance, validated_data):
        instance.is_kyc_verified = False
        instance.kyc_rejection_reason = validated_data["kyc_rejection_reason"]
        instance.save()
        return instance


class DocumentUploadSerializer(serializers.Serializer):
    document = serializers.FileField(required=True)

    # def validate_document(self, value):
    #     ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "application/pdf"]
    #     if value.content_type not in ALLOWED_FILE_TYPES:
    #         raise serializers.ValidationError(
    #             "Invalid file format. Allowed: JPEG, PNG, PDF"
    #         )
    #     return value


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
