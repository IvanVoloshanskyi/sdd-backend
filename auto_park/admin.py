from django.contrib import admin

from auto_park.car_model import Car, CarType, CarBrand
from auto_park.models import AutoPark
from auto_park.rent import Rent


class RentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'car',
        'auto_park',
        'rental_date',
        'expected_return_date',
        'return_date',
        'deposit_returned',
        'rental_cost'
    )


# Register your models here.
admin.site.register(AutoPark)
admin.site.register(Car)
admin.site.register(CarBrand)
admin.site.register(CarType)
admin.site.register(Rent, RentAdmin)
