# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import User , AnonymousUser ,OTP

class UserAdmin(admin.ModelAdmin):
    list_display = ('email',)  # Display email in the list view
    search_fields = ('email',)  # Enable search by email
    ordering = ('email',)  # Order by email

    fieldsets = (
        (None, {
            'fields': ('email', 'password','camera_id','is_permission')
        }),
    )
     # Password should not be editable in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password')}
        ),
    )

    def save_model(self, request, obj, form, change):
     
        super().save_model(request, obj, form, change)

admin.site.register(User, UserAdmin)


admin.site.register(AnonymousUser)
admin.site.register(OTP)