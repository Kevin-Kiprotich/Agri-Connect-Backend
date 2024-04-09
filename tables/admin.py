from django.contrib import admin
from .models import SUMS
# Register your models here.
class SUMSAdmin(admin.ModelAdmin):
    list_display=['grantee','quota','year','file']


admin.site.register(SUMS,SUMSAdmin)