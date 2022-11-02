from django.contrib import admin
from .models import Car, Order, PrivateMsg, Driver
# Register your models here.

class CarAdmin(admin.ModelAdmin):
    list_display = ("car_name", "image", "company_name", "cost_par_day")
class OrderAdmin(admin.ModelAdmin):
    list_display = ("car_name", "date", "to", "driver")
class DriverAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "id_number", "phone_number")

class PrivateMsgAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "message")


admin.site.register(Driver, DriverAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(PrivateMsg, PrivateMsgAdmin)