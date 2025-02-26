from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "full_name",
        "phone_number",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    readonly_fields = ["last_login", "date_joined"]
    list_per_page = 10
    search_fields = ["full_name"]
    list_filter = ["is_staff", "is_superuser", "is_active"]

    # fieldsets is the form for editing or viewing an entity
    # the first index of each tuple is the name of the section: ex. 'Personal Information', 'Role Status'
    fieldsets = (
        (
            "Peronal Information",
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "full_name",
                    "email",
                    "password",
                    "document",
                ),
            },
        ),
        (
            "Role Status",
            {
                "classes": ("wide",),
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
        (
            "Permissions",
            {
                "classes": ("wide",),
                "fields": ("groups", "user_permissions"),
            },
        ),
        (
            "Date Information",
            {
                "classes": ("wide",),
                "fields": ("last_login", "date_joined"),
            },
        ),
    )

    # add_fieldsets is the form for adding/creating a new entity
    # the first index of each tuple is the name of the section: ex. 'Personal Information', 'Role Status'
    add_fieldsets = (
        (
            "Peronal Information",
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "full_name",
                    "email",
                    "password1",
                    "password2",
                    "document",
                ),
            },
        ),
        (
            "Role Status",
            {
                "classes": ("wide",),
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
        (
            "Permissions",
            {
                "classes": ("wide",),
                "fields": ("groups", "user_permissions"),
            },
        ),
    )

    # table should be ordered by name
    ordering = ("full_name",)
    # search by email, name
    search_fields = ("full_name",)
