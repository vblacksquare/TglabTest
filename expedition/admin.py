from django.contrib import admin
from .models import Expedition, ExpeditionMember

# Register your models here.

admin.site.register(Expedition)
admin.site.register(ExpeditionMember)
