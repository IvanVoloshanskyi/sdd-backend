from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from auto_park.models import AutoPark


@api_view(['GET'])
def auto_park_list(request, auto_park_slug):
    auto_parks = AutoPark.objects.prefetch_related('cars').filter(slug=auto_park_slug)
    data = []

    for auto_park in auto_parks:
        park_data = {
            'id': auto_park.id,
            'slug': auto_park.slug,
            'cars': []
        }

        for car in auto_park.cars.all():
            car_data = {
                'id': car.id,
                'name': car.name,
                'year': car.year,
                'price_per_day': car.price_per_day,
                'car_brand': car.car_brand.title,
                'car_type': car.car_type.title,
                'penalty_amount': car.penalty_amount
            }
            park_data['cars'].append(car_data)

        data.append(park_data)

    return Response(data)


@api_view(['GET'])
def car_detail(request, auto_park_slug, car_id):
    auto_park = get_object_or_404(AutoPark, slug=auto_park_slug)
    car = get_object_or_404(auto_park.cars, id=car_id)

    car_data = {
        'id': car.id,
        'name': car.name,
        'year': car.year,
        'price_per_day': car.price_per_day,
        'car_brand': car.car_brand.title,
        'car_type': car.car_type.title,
        'penalty_amount': car.penalty_amount
    }

    return Response(car_data)