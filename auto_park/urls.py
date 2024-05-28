from django.urls import path
from auto_park.views import get_all_auto_park_cars, car_detail, get_all_unrented_cars, car_availability_report, car_financial_report
from auto_park.rent import rent_car, return_car, get_user_rent_list

urlpatterns = [
    path('auto-park-list/<slug:auto_park_slug>/', get_all_auto_park_cars, name='auto_park_list'),
    path('auto-park-car/<slug:auto_park_slug>/<int:car_id>/', car_detail, name='auto_park_list'),
    path('auto-park-unrented-cars/<slug:auto_park_slug>/', get_all_unrented_cars, name='auto_park_list'),

    path('rent-car/<slug:auto_park_slug>/<int:car_id>/', rent_car, name='rent_car'),
    path('rent-list/', get_user_rent_list, name='rent_list'),
    path('return-car/<int:rent_id>/', return_car, name='return_car'),

    path('reports/<slug:auto_park_slug>/car-availability/', car_availability_report, name='car_availability_report'),
    path('reports/<slug:auto_park_slug>/car-financial/', car_financial_report, name='car_financial_report'),
]