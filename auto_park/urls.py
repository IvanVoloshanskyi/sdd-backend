from django.urls import path
from auto_park.views import auto_park_list, car_detail
from auto_park.rent import rent_car, return_car, car_availability_report, car_financial_report

urlpatterns = [
    path('auto-park-list/<slug:auto_park_slug>/', auto_park_list, name='auto_park_list'),
    path('auto-park-car/<slug:auto_park_slug>/<int:car_id>/', car_detail, name='auto_park_list'),

    path('rent-car/<slug:auto_park_slug>/<int:car_id>/', rent_car, name='rent_car'),
    path('return-car/<int:rent_id>/', return_car, name='return_car'),

    path('reports/<slug:auto_park_slug>/car-availability/', car_availability_report, name='car_availability_report'),
    path('reports/<slug:auto_park_slug>/car-financial/', car_financial_report, name='car_financial_report'),
]