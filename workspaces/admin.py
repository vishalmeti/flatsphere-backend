# workspaces/admin.py
from django.contrib import admin
from .models import Workspace, UserWorkspace, ApartmentUnit

admin.site.register(Workspace)
admin.site.register(UserWorkspace)
admin.site.register(ApartmentUnit)
