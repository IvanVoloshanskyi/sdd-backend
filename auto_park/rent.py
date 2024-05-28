from datetime import datetime
from decimal import Decimal

from django.contrib.sessions.models import Session
from django.db import models, transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from auth_user.models import CustomUser
from auto_park.car_model import Car
from auto_park.models import AutoPark, AutoParkCar


class Rent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    auto_park = models.ForeignKey(AutoPark, on_delete=models.CASCADE)
    rental_date = models.DateTimeField(default=timezone.now)
    expected_return_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    deposit_returned = models.BooleanField(default=False)
    deposit_amount = models.IntegerField(default=0)
    rental_cost = models.IntegerField(default=0)
    penalty_cost = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} rented {self.car} in {self.auto_park.slug}"

    def calculate_rental_cost(self):
        rental_duration = (self.expected_return_date - self.rental_date).days + 1
        car_age = timezone.now().year - self.car.year
        base_cost = rental_duration * self.car.price_per_day
        age_discount = Decimal('0.05') * Decimal(car_age)  # 5% знижка за кожен рік старіння автомобіля
        final_cost = base_cost * (Decimal('1') - age_discount)

        self.rental_cost = max(final_cost, Decimal('0'))  # Вартість не може бути негативною
        self.save()

    def calculate_penalty_amount(self):
        days_difference = (self.return_date.date() - self.expected_return_date.date()).days
        if days_difference > 0:
            self.penalty_cost = days_difference * self.car.penalty_amount
        else:
            self.penalty_cost = 0
        return self.penalty_cost


@api_view(['POST'])
@transaction.atomic
def rent_car(request, auto_park_slug, car_id):
    try:
        car = AutoParkCar.objects.select_for_update().get(pk=car_id)
    except AutoParkCar.DoesNotExist:
        return JsonResponse({'error': 'Car object does not exist'}, status=404)

    try:
        auto_park = AutoPark.objects.get(slug=auto_park_slug)
    except AutoPark.DoesNotExist:
        return JsonResponse({'error': 'Auto park object does not exist'}, status=404)

    if car.auto_park != auto_park:
        return JsonResponse({'error': 'Car does not belong to the specified auto park'}, status=400)

    try:
        session_key = request.session.session_key
        session = Session.objects.get(session_key=session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User object does not exist'}, status=404)
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session object does not exist'}, status=404)

    data = request.data
    rental_date_str = data.get('rental_date')
    expected_return_date_str = data.get('expected_return_date')
    deposit_amount = data.get('deposit_amount')

    if not rental_date_str:
        return JsonResponse({'error': 'Rental date is required'}, status=400)
    if not expected_return_date_str:
        return JsonResponse({'error': 'Expected return date is required'}, status=400)
    if not deposit_amount:
        return JsonResponse({'error': 'Deposit amount is required'}, status=400)

    try:
        rental_date = datetime.strptime(rental_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid rental date format, should be YYYY-MM-DD'}, status=400)

    try:
        expected_return_date = datetime.strptime(expected_return_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid expected return date format, should be YYYY-MM-DD'}, status=400)

    if expected_return_date < timezone.now().date():
        return JsonResponse({'error': 'Expected return date must be in the future'}, status=400)

    active_rents = Rent.objects.filter(user=user, car=car.car, return_date__isnull=True)
    if active_rents.exists():
        return JsonResponse({'error': 'You already have an active rent for this car'}, status=400)

    with transaction.atomic():
        car.save()

        rent = Rent.objects.create(
            user=user,
            car=car.car,
            auto_park=auto_park,
            rental_date=rental_date,
            expected_return_date=expected_return_date,
            deposit_amount=deposit_amount,
        )
        rent.calculate_rental_cost()

    return JsonResponse({'success': 'Car rented successfully'}, status=201)


@api_view(['POST'])
def return_car(request, rent_id):
    try:
        rent = Rent.objects.get(pk=rent_id)
    except Rent.DoesNotExist:
        return JsonResponse({'error': 'Rent object does not exist'}, status=404)

    try:
        session_key = request.session.session_key
        session = Session.objects.get(session_key=session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User object does not exist'}, status=404)
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session object does not exist'}, status=404)

    if rent.user != user:
        return JsonResponse({'error': 'You do not have permission to return this car'}, status=403)

    if rent.return_date:
        return JsonResponse({'error': 'That car has returned'}, status=404)

    autopark_car = AutoParkCar.objects.get(auto_park=rent.auto_park, car=rent.car)
    rent.return_date = timezone.now()
    calculate_penalty = rent.calculate_penalty_amount()
    rent.deposit_returned = True
    autopark_car.save()
    rent.save()

    return JsonResponse({'success': 'Car returned successfully', 'penalty': calculate_penalty}, status=201)


@api_view(['GET'])
def get_user_rent_list(request):
    try:
        session_key = request.session.session_key
        session = Session.objects.get(session_key=session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User object does not exist'}, status=404)
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Session object does not exist'}, status=404)

    rents = Rent.objects.filter(user=user)
    rent_list = []
    for rent in rents:
        is_rented = True if not rent.return_date else False

        rent_data = {
            'id': rent.id,
            'user_id': rent.user.id,
            'car_id': rent.car.id,
            'auto_park_id': rent.auto_park.id,
            'rental_date': rent.rental_date,
            'expected_return_date': rent.expected_return_date,
            'return_date': rent.return_date,
            'deposit_returned': rent.deposit_returned,
            'deposit_amount': rent.deposit_amount,
            'rental_cost': rent.rental_cost,
            'is_rented': is_rented,
        }
        rent_list.append(rent_data)
    return Response(rent_list)
