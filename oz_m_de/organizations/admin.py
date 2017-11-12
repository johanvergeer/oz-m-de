from django.contrib import admin

# Register your models here.
from .models import Organization, OrganizationCategory

admin.site.register(Organization)
admin.site.register(OrganizationCategory)
