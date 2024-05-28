from abc import ABC, abstractmethod
from rest_framework.response import Response
from auto_park.models import AutoPark
from auto_park.rent import Rent
from django.db.models import Sum


class CarReport(ABC):
 
    def generate_report(self, auto_park_slug):
        try:
            auto_park = AutoPark.objects.get(slug=auto_park_slug)
        except AutoPark.DoesNotExist:
            return Response({'error': 'Auto park does not exist'}, status=404)

        cars = auto_park.cars.all()
        report = []

        for car in cars:
            report.append(self.get_data(car))

        return Response(report)
    
    @abstractmethod
    def get_data(self, car):
        pass


class CarAvailabilityReport(CarReport):

    def get_data(self, car):
        total_rents = Rent.objects.filter(car=car).count()
        active_rents = Rent.objects.filter(car=car, return_date__isnull=True).count()
        availability_status = 'available' if active_rents == 0 else 'rented'

        return {
            'car_id': car.id,
            'car_name': car.car_brand.title + ' ' + car.name,
            'total_rents': total_rents,
            'active_rents': active_rents,
            'availability_status': availability_status,
        }
    

class CarFinancialReport(CarReport):

    def get_data(self, car):
        total_income = Rent.objects.filter(car=car).aggregate(total_income=Sum('rental_cost'))['total_income'] or 0
        total_penalties = Rent.objects.filter(car=car).aggregate(total_penalties=Sum('penalty_cost'))[
                              'total_penalties'] or 0

        return {
            'car_id': car.id,
            'car_name': car.car_brand.title + ' ' + car.name,
            'total_income': total_income,
            'total_penalties': total_penalties,
        }
