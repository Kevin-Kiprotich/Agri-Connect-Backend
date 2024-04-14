from django.contrib import admin
from .models import SUMS,AnnualTotals
# Register your models here.
class SUMSAdmin(admin.ModelAdmin):
    list_display=['grantee','quota','year','file']

class AnnualTotalsAdmin(admin.ModelAdmin):
    list_display=['grantee','year','file']


# Register the sites backend for admin
admin.site.register(SUMS,SUMSAdmin)
admin.site.register(AnnualTotals,AnnualTotalsAdmin)