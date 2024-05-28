from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.sessions.models import Session
from django.http import JsonResponse

from auto_park.models import AutoPark, AutoParkCar
from auto_park.car_report import CarAvailabilityReport, CarFinancialReport


@api_view(['GET'])
def get_all_auto_park_cars(request, auto_park_slug):
    try:
        session_key = request.headers.get('X-Session-Key', request.session.session_key)
        session = Session.objects.get(session_key=session_key)  
    except Session.DoesNotExist:    
        return JsonResponse({'error': 'Session object does not exist'}, status=404)

    auto_park = get_object_or_404(AutoPark, slug=auto_park_slug)
    all_cars = AutoParkCar.objects.filter(auto_park=auto_park).select_related(
        'car__car_brand',
        'car__car_type'
    )
    data = []

    park_data = {
        'id': auto_park.id,
        'slug': auto_park.slug,
        'cars': []
    }

    for auto_park_car in all_cars:
        car = auto_park_car.car
        car_data = {
            'id': car.id,
            'name': car.name,
            'year': car.year,
            'price_per_day': car.price_per_day,
            'car_brand': car.car_brand.title,
            'car_type': car.car_type.title,
            'penalty_amount': car.penalty_amount,
            'rented': auto_park_car.is_rented
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
        'penalty_amount': car.penalty_amount,

    }

    return Response(car_data)


@api_view(['GET'])
def get_all_unrented_cars(request, auto_park_slug):
    auto_park = get_object_or_404(AutoPark, slug=auto_park_slug)

    unrented_cars = AutoParkCar.objects.filter(auto_park=auto_park, is_rented=False).select_related(
        'car__car_brand',
        'car__car_type'
    )

    auto_park_data = {
        'id': auto_park.id,
        'slug': auto_park.slug,
        'cars': []
    }

    for auto_park_car in unrented_cars:
        car = auto_park_car.car
        car_data = {
            'id': car.id,
            'name': car.name,
            'year': car.year,
            'price_per_day': car.price_per_day,
            'car_brand': car.car_brand.title,
            'car_type': car.car_type.title,
            'penalty_amount': car.penalty_amount,
        }
        auto_park_data['cars'].append(car_data)

    return Response(auto_park_data)


@api_view(['GET'])
def car_availability_report(request, auto_park_slug):
    try:
        session_key = request.headers.get('X-Session-Key', request.session.session_key)
        session = Session.objects.get(session_key=session_key)  
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session object does not exist'}, status=404)
    
    return CarAvailabilityReport().generate_report(auto_park_slug)


@api_view(['GET'])
def car_financial_report(request, auto_park_slug):
    try:
        session_key = request.headers.get('X-Session-Key', request.session.session_key)
        session = Session.objects.get(session_key=session_key)  
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session object does not exist'}, status=404)
    
    return CarFinancialReport().generate_report(auto_park_slug)