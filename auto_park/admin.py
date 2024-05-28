from django.contrib import admin

from auto_park.car_model import Car, CarType, CarBrand
from auto_park.models import AutoPark, AutoParkCar
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

    search_fields = ('user__username', 'user__email',)
    list_filter = ('user__username',)


class AutoParkCarAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'auto_park',
        'car',
    )
    list_filter = ('auto_park__slug',)


class CarAdmin(admin.ModelAdmin):
    list_display = (
        'car_brand',
        'name',
        'car_type',
        'year',
        'price_per_day',
        'penalty_amount',
    )
    list_filter = ('car_brand',)


class HiddenModelAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

    def has_view_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(AutoParkCar, AutoParkCarAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Rent, RentAdmin)
admin.site.register(CarBrand, HiddenModelAdmin)
admin.site.register(CarType, HiddenModelAdmin)
admin.site.register(AutoPark, HiddenModelAdmin)
