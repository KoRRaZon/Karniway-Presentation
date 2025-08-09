from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import CustomUser, Player, Master


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'account_type', 'created_at')
    list_filter = ('is_staff', 'is_active', 'account_type', 'created_at')
    ordering = ('-email',)

    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'account_type')}),
        ('Важные даты', {'fields': ('created_at', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password', 'password_confirm', 'is_staff', 'account_type')
        }),
    )

    search_fields = ('email', 'first_name', 'last_name', 'account_type')


@admin.register(Player)
class CustomUserAdmin(ModelAdmin):
    pass

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    pass
