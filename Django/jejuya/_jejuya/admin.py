from django.contrib import admin
from .models import *

class ACCOUNTAdmin(admin.ModelAdmin):
    list_display = ['id', 'account_type', 'dt']
    list_filter = ['account_type']
    search_fields = ['id']
admin.site.register(ACCOUNT, ACCOUNTAdmin)

class SCHEDULEAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'date']
    list_filter = ['date']
    search_fields = ['id', 'user_id', 'date']
admin.site.register(SCHEDULE, SCHEDULEAdmin)

class SCHEDULE_ITEMAdmin(admin.ModelAdmin):
    list_display = ['id', 'schedule_id', 'around_id', 'order']
    search_fields = ['id', 'schedule_id', 'around_id']
admin.site.register(SCHEDULE_ITEM, SCHEDULE_ITEMAdmin)

class POINTAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'rooms_cnt', 'tel']
    search_fields = ['id', 'name', 'address']
admin.site.register(POINT, POINTAdmin)

class AROUNDAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'around_type', 'categories']
    list_filter = ['around_type', 'categories']
    search_fields = ['id', 'name', 'address', 'around_type', 'categories']
admin.site.register(AROUND, AROUNDAdmin)