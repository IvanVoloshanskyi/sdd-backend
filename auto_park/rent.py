from datetime import datetime
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from auth_user.models import CustomUser
from auto_park.car_model import Car
from auto_park.models import AutoPark


class Rent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    auto_park = models.ForeignKey(AutoPark, on_delete=models.CASCADE)
    rental_date = models.DateTimeField(default=timezone.now)
    expected_return_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    deposit_returned = models.BooleanField(default=False)
    rental_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user} rented {self.car} in {self.auto_park.slug}"

    def calculate_rental_cost(self):
        rental_duration = (self.expected_return_date - self.rental_date.date()).days + 1
        car_age = timezone.now().year - self.car.year
        base_cost = rental_duration * self.car.price_per_day
        age_discount = Decimal('0.05') * Decimal(car_age)  # 5% знижка за кожен рік старіння автомобіля
        final_cost = base_cost * (Decimal('1') - age_discount)

        self.rental_cost = max(final_cost, Decimal('0'))  # Вартість не може бути негативною
        self.save()

    def calculate_penalty_amount(self):
        days_difference = (self.return_date.date() - self.expected_return_date.date()).days
        if days_difference > 0:
            self.penalty_amount = days_difference * self.car.penalty_amount
        else:
            self.car.penalty_amount = 0


@api_view(['POST'])
def rent_car(request, auto_park_slug, car_id):
    try:
        car = Car.objects.get(pk=car_id)
    except Car.DoesNotExist:
        return JsonResponse({'error': 'car object does not exist'}, status=404)

    try:
        auto_park = AutoPark.objects.get(slug=auto_park_slug)
    except AutoPark.DoesNotExist:
        return JsonResponse({'error': 'auto_park object does not exist'}, status=404)

    if car not in auto_park.cars.all():
        return JsonResponse({'error': 'car does not belong to the specified auto_park'}, status=400)

    try:
        user = CustomUser.objects.get(pk=request.user.id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'user object does not exist'}, status=404)

    data = request.data
    expected_return_date_str = data.get('expected_return_date')

    try:
        expected_return_date = datetime.strptime(expected_return_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format, should be YYYY-MM-DD'}, status=400)

    if not expected_return_date:
        return JsonResponse({'error': 'Expected date is required'}, status=404)

    if expected_return_date < timezone.now().date():
        return JsonResponse({'error': 'Expected date must be in the future'}, status=400)

    rent = Rent.objects.create(
        user=user,
        car=car,
        auto_park=auto_park,
        rental_date=timezone.now(),
        expected_return_date=expected_return_date,
    )
    rent.calculate_rental_cost()

    return JsonResponse({'success': 'Car rented successfully'}, status=201)


@api_view(['POST'])
def return_car(request, rent_id):
    try:
        rent = Rent.objects.get(pk=rent_id)
    except Rent.DoesNotExist:
        return JsonResponse({'error': 'Rent object does not exist'}, status=404)

    if rent.user != request.user:
        return JsonResponse({'error': 'You do not have permission to return this car'}, status=403)

    rent.return_date = timezone.now()
    rent.calculate_penalty_amount()
    rent.deposit_returned = True
    rent.save()

    return JsonResponse({'success': 'Car returned successfully'}, status=201)


@api_view(['GET'])
def car_availability_report(request, auto_park_slug):
    try:
        auto_park = AutoPark.objects.get(slug=auto_park_slug)
    except AutoPark.DoesNotExist:
        return Response({'error': 'Auto park does not exist'}, status=404)

    cars = auto_park.cars.all()
    report = []

    for car in cars:
        total_rents = Rent.objects.filter(car=car).count()
        active_rents = Rent.objects.filter(car=car, return_date__isnull=True).count()
        availability_status = 'available' if active_rents == 0 else 'rented'

        report.append({
            'car_id': car.id,
            'car_name': car.name,
            'total_rents': total_rents,
            'active_rents': active_rents,
            'availability_status': availability_status,
        })

    return Response(report)


@api_view(['GET'])
def car_financial_report(request, auto_park_slug):
    try:
        auto_park = AutoPark.objects.get(slug=auto_park_slug)
    except AutoPark.DoesNotExist:
        return Response({'error': 'Auto park does not exist'}, status=404)

    cars = auto_park.cars.all()
    report = []

    for car in cars:
        total_income = Rent.objects.filter(car=car).aggregate(total_income=Sum('rental_cost'))['total_income'] or 0
        total_penalties = Rent.objects.filter(car=car).aggregate(total_penalties=Sum('car__penalty_amount'))[
                              'total_penalties'] or 0

        report.append({
            'car_id': car.id,
            'car_name': car.name,
            'total_income': total_income,
            'total_penalties': total_penalties,
        })

    return Response(report)