"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from accounts.views import (
    RegisterView,
    LogoutView,
    KYCStatusView,
    UserProfileView,
    UsersView,
    ApproveKYCView,
    RejectKYCView,
    VerifyIdentityView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    # TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/signup/", RegisterView.as_view(), name="signup"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/kyc-status/", KYCStatusView.as_view(), name="kyc-status"),
    path("api/user-profile/", UserProfileView.as_view(), name="user-profile"),
    path("api/admin/users/", UsersView.as_view(), name="all-users"),
    path(
        "api/admin/approve-kyc/<int:pk>/", ApproveKYCView.as_view(), name="approve-kyc"
    ),
    path("api/admin/reject-kyc/<int:pk>/", RejectKYCView.as_view(), name="reject-kyc"),
    path("api/upload-document/", VerifyIdentityView.as_view(), name="verify-identity"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns = [path("__debug__/", include("debug_toolbar.urls"))] + urlpatterns
