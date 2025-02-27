# from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    RegistrationSerializer,
    UserProfileSerializer,
    ApproveKYCSerializer,
    RejectKYCSerializer,
    DocumentUploadSerializer,
    RefreshTokenSerializer,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .utils import (
    extract_text_from_ID,
    extract_face_from_ID,
    is_name_matching,
)
from django.core.files.base import ContentFile
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="User Registration",
        description="Registers a new user with phone number, password, full name, and document.",
        request=RegistrationSerializer,
        responses={
            201: OpenApiResponse(
                response={"status": "string"},
                description="User registered successfully.",
                examples=[
                    OpenApiExample(
                        "Successful Registration",
                        value={"status": "success"},
                        response_only=True,
                        status_codes=[201],
                    )
                ],
            ),
            400: OpenApiResponse(
                response={"error": "string"},
                description="Invalid input data.",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={"error": "Phone number is required."},
                        response_only=True,
                        status_codes=[400],
                    ),
                    OpenApiExample(
                        "Invalid Document Upload",
                        value={
                            "error": "Invalid file format. Only PDFs and images are allowed."
                        },
                        response_only=True,
                        status_codes=[400],
                    ),
                ],
            ),
        },
    )
    def post(self, request):
        """
        Handle POST request for user registration.

        This method processes the registration data sent in the request,
        validates it using the RegistrationSerializer, and saves the new user
        if the data is valid. Upon successful registration, it returns a
        response with a status of "success" and HTTP status code 201 (Created).

        Args:
            request (Request): The HTTP request object containing registration data.

        Returns:
            Response: A response object with a success message and HTTP status code 201.
        """
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="User Logout",
        description="Logs out the user by blacklisting the provided refresh token.",
        request=RefreshTokenSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "string"},
                description="User successfully logged out.",
                examples=[
                    OpenApiExample(
                        "Successful Logout",
                        value={"status": "logout success"},
                        response_only=True,
                        status_codes=[200],
                    )
                ],
            ),
            400: OpenApiResponse(
                response={"error": "string"},
                description="No refresh token provided.",
                examples=[
                    OpenApiExample(
                        "Missing Refresh Token",
                        value={"refresh": ["This field is required."]},
                        response_only=True,
                        status_codes=[400],
                    ),
                ],
            ),
            401: OpenApiResponse(
                response={"error": "string"},
                description="User is not authenticated.",
                examples=[
                    OpenApiExample(
                        "Unauthorized Request",
                        value={
                            "error": "Authentication credentials were not provided."
                        },
                        response_only=True,
                        status_codes=[401],
                    ),
                    OpenApiExample(
                        "Invalid Authentication",
                        value={"error": "Invalid or expired authentication token."},
                        response_only=True,
                        status_codes=[401],
                    ),
                ],
            ),
        },
    )
    def post(self, request):
        """
        Handle POST request to log out a user by blacklisting the refresh token.

        Args:
            request (Request): The HTTP request object containing the refresh token.

        Returns:
            Response: A response indicating the success or failure of the logout operation.
            - On success: Returns a response with status 200 and a message "logout success".
            - On failure: Returns a response with status 400 and an error message.

        Raises:
            Exception: If an error occurs during the process, an error response is returned.
        """
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"status": "logout success"}, status=200)
        except Exception:
            return Response(
                {"error": "An error occurred, please try again."}, status=400
            )


class KYCStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve KYC Verification Status",
        description="Returns the KYC verification status of the authenticated user.",
        responses={
            200: OpenApiResponse(
                response={"status": "string"},
                description="KYC verification status retrieved successfully.",
                examples=[
                    OpenApiExample(
                        "Verified User",
                        value={"status": "Verified"},
                        response_only=True,
                        status_codes=[200],
                    ),
                    OpenApiExample(
                        "Not Verified User",
                        value={"status": "Not Verified"},
                        response_only=True,
                        status_codes=[200],
                    ),
                ],
            ),
            401: OpenApiResponse(
                response={"error": "string"},
                description="User is not authenticated.",
                examples=[
                    OpenApiExample(
                        "Unauthorized Request",
                        value={
                            "error": "Authentication credentials were not provided."
                        },
                        response_only=True,
                        status_codes=[401],
                    ),
                    OpenApiExample(
                        "Invalid Authentication",
                        value={"error": "Invalid or expired authentication token."},
                        response_only=True,
                        status_codes=[401],
                    ),
                ],
            ),
        },
    )
    def get(self, request):
        """
        Handle GET request to retrieve the KYC verification status of the user.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: A JSON response containing the KYC verification status of the user.
                      The response includes a "status" key with the value "Verified" if the user
                      is KYC verified, otherwise "Not Verified". The response status code is 200 OK.
        """
        user = self.request.user
        return Response(
            {"status": "Verified" if user.is_kyc_verified else "Not Verified"},
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve User Profile",
        description="Returns the profile details of the authenticated user.",
        responses={
            200: OpenApiResponse(
                response=UserProfileSerializer,
                description="User profile retrieved successfully.",
                examples=[
                    OpenApiExample(
                        "Example User Profile",
                        value={
                            "id": 1,
                            "full_name": "John Doe",
                            "phone_number": "+1234567890",
                            "email": "johndoe@example.com",
                            "is_kyc_verified": True,
                            "kyc_rejection_reason": "",
                            "profile_photo": "",
                            "document": "",
                        },
                        response_only=True,
                        status_codes=[200],
                    ),
                ],
            ),
            401: OpenApiResponse(
                response={"error": "string"},
                description="User is not authenticated.",
                examples=[
                    OpenApiExample(
                        "Unauthorized Request",
                        value={
                            "error": "Authentication credentials were not provided."
                        },
                        response_only=True,
                        status_codes=[401],
                    ),
                    OpenApiExample(
                        "Invalid Authentication",
                        value={"error": "Invalid or expired authentication token."},
                        response_only=True,
                        status_codes=[401],
                    ),
                ],
            ),
        },
    )
    def get(self, request):
        """
        Handle GET request to retrieve the user profile.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: A Response object containing the serialized user profile data and HTTP status 200 (OK).
        """
        user = self.request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Retrieve All Users",
        description="Returns a list of all registered users. Admin access required.",
        responses={
            200: OpenApiResponse(
                response=UserProfileSerializer(many=True),
                description="List of user profiles retrieved successfully.",
                examples=[
                    OpenApiExample(
                        "Example List of Users",
                        value=[
                            {
                                "id": 1,
                                "full_name": "John Doe",
                                "phone_number": "+1234567890",
                                "email": "johndoe@example.com",
                                "is_kyc_verified": False,
                                "kyc_rejection_reason": "",
                                "profile_photo": "",
                                "document": "",
                            },
                            {
                                "id": 2,
                                "full_name": "Jane Smith",
                                "phone_number": "+9876543210",
                                "email": "janesmith@example.com",
                                "is_kyc_verified": False,
                                "kyc_rejection_reason": "",
                                "profile_photo": "",
                                "document": "",
                            },
                        ],
                        response_only=True,
                        status_codes=[200],
                    ),
                ],
            ),
            401: OpenApiResponse(
                response={"error": "string"},
                description="User is not authenticated.",
                examples=[
                    OpenApiExample(
                        "Unauthorized Request",
                        value={
                            "error": "Authentication credentials were not provided."
                        },
                        response_only=True,
                        status_codes=[401],
                    ),
                ],
            ),
            403: OpenApiResponse(
                response={"error": "string"},
                description="User does not have permission to access this resource.",
                examples=[
                    OpenApiExample(
                        "Forbidden Access",
                        value={
                            "error": "You do not have permission to perform this action."
                        },
                        response_only=True,
                        status_codes=[403],
                    ),
                ],
            ),
        },
    )
    def get(self, request):
        """
        Handles GET requests to retrieve all user profiles.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: A Response object containing serialized user profile data
                      and an HTTP 200 OK status.
        """
        users = User.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApproveKYCView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Approve KYC Verification",
        description="Approves the KYC verification for a specific user. Admin access required.",
        request=ApproveKYCSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="User KYC verification approved successfully.",
                examples=[
                    OpenApiExample(
                        "Successful KYC Approval",
                        value={"status": "success"},
                        response_only=True,
                        status_codes=[200],
                    ),
                ],
            ),
            400: OpenApiResponse(
                response={"error": "Validation error message"},
                description="Invalid input data.",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={"error": "Invalid data provided."},
                        response_only=True,
                        status_codes=[400],
                    ),
                ],
            ),
            404: OpenApiResponse(
                response={"error": "User not found"},
                description="The specified user does not exist.",
                examples=[
                    OpenApiExample(
                        "User Not Found",
                        value={"error": "User with the given ID does not exist."},
                        response_only=True,
                        status_codes=[404],
                    ),
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Permission denied"},
                description="User does not have the required permissions.",
                examples=[
                    OpenApiExample(
                        "Forbidden Access",
                        value={
                            "error": "You do not have permission to perform this action."
                        },
                        response_only=True,
                        status_codes=[403],
                    ),
                ],
            ),
        },
    )
    def post(self, request, pk):
        """
        Handle POST request to approve KYC verification for a user.

        Args:
            request (Request): The HTTP request object containing the data for KYC approval.
            pk (int): The primary key of the user whose KYC is being approved.

        Returns:
            Response: A response object with a success status and HTTP 200 OK status code.

        Raises:
            Http404: If the user with the specified primary key does not exist.
            ValidationError: If the provided data is not valid according to the serializer.
        """
        user = get_object_or_404(User, pk=pk)
        serializer = ApproveKYCSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response({"status": "success"}, status=status.HTTP_200_OK)


class RejectKYCView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Reject KYC Verification",
        description="Rejects the KYC verification for a specific user. Admin access required.",
        request=RejectKYCSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="User KYC verification rejected successfully.",
                examples=[
                    OpenApiExample(
                        "Successful KYC Rejection",
                        value={"status": "success"},
                        response_only=True,
                        status_codes=[200],
                    ),
                ],
            ),
            400: OpenApiResponse(
                response={"error": "Validation error message"},
                description="Invalid input data.",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={"error": "Invalid data provided."},
                        response_only=True,
                        status_codes=[400],
                    ),
                ],
            ),
            404: OpenApiResponse(
                response={"error": "User not found"},
                description="The specified user does not exist.",
                examples=[
                    OpenApiExample(
                        "User Not Found",
                        value={"error": "User with the given ID does not exist."},
                        response_only=True,
                        status_codes=[404],
                    ),
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Permission denied"},
                description="User does not have the required permissions.",
                examples=[
                    OpenApiExample(
                        "Forbidden Access",
                        value={
                            "error": "You do not have permission to perform this action."
                        },
                        response_only=True,
                        status_codes=[403],
                    ),
                ],
            ),
        },
    )
    def post(self, request, pk):
        """
        Handle POST request to reject KYC verification for a user.

        Args:
            request (Request): The HTTP request object containing the data.
            pk (int): The primary key of the user whose KYC verification is to be rejected.

        Returns:
            Response: A response object with a success status and HTTP 200 OK status code.

        Raises:
            Http404: If the user with the given primary key does not exist.
            ValidationError: If the provided data is not valid.
        """
        user = get_object_or_404(User, pk=pk)
        serializer = RejectKYCSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user, serializer.validated_data)
        return Response({"status": "success"}, status=status.HTTP_200_OK)


class VerifyIdentityView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Verify User Identity",
        description=(
            "Uploads a document for KYC verification. Extracts text and profile picture, "
            "compares extracted name with user's name, and marks the user as verified if they match."
        ),
        request=DocumentUploadSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "Verification successful!"},
                description="The user's identity has been successfully verified.",
                examples=[
                    OpenApiExample(
                        "Successful Verification",
                        value={"status": "Verification successful!"},
                        response_only=True,
                        status_codes=[200],
                    ),
                ],
            ),
            400: OpenApiResponse(
                response={"error": "Full name does not match ID."},
                description="The name extracted from the document does not match the user's full name.",
                examples=[
                    OpenApiExample(
                        "Name Mismatch",
                        value={"error": "Full name does not match ID."},
                        response_only=True,
                        status_codes=[400],
                    ),
                    OpenApiExample(
                        "Invalid Document Format",
                        value={"error": "Uploaded document is not valid."},
                        response_only=True,
                        status_codes=[400],
                    ),
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Permission denied"},
                description="User does not have permission to perform this action.",
                examples=[
                    OpenApiExample(
                        "Unauthorized Access",
                        value={
                            "error": "You do not have permission to perform this action."
                        },
                        response_only=True,
                        status_codes=[403],
                    ),
                ],
            ),
        },
    )
    def post(self, request):
        """
        Handle POST request for document upload and KYC verification.

        This method performs the following steps:
        1. Deserialize the incoming request data using DocumentUploadSerializer.
        2. Validate the serializer data.
        3. Extract text and profile picture from the uploaded document.
        4. Check if the extracted name matches the user's full name.
        5. Save the extracted profile picture to the user's profile.
        6. Mark the user as KYC verified.
        7. Return a success response if verification is successful, otherwise return an error response.

        Args:
            request (Request): The HTTP request object containing the document data.

        Returns:
            Response: A Response object with the status of the verification process.
        """
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        document = serializer.validated_data["document"]
        user = request.user

        extracted_text = extract_text_from_ID(document)
        profile_picture = extract_face_from_ID(document)

        if not is_name_matching(user.full_name, extracted_text):
            send_mail(
                subject="Document Rejected",
                message="Greetings,\n\nKindly note your verification has been rejected as your name does not match the name on the ID provided.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response(
                {"error": "Full name does not match ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.profile_photo.save(f"{user.id}_profile.jpg", ContentFile(profile_picture))

        user.is_kyc_verified = True
        user.save()

        return Response(
            {"status": "Verification successful!"}, status=status.HTTP_200_OK
        )
