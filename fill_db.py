import random
from django.utils import timezone
from faker import Faker

from auth_user.models import CustomUser
from auto_park.models import AutoPark, Car, AutoParkCar
from auto_park.car_model import CarBrand, CarType
from auto_park.rent import Rent

fake = Faker()

fake = Faker()


def create_auto_parks_with_cars(num_auto_parks=5, num_cars_per_auto_park=10):
    for _ in range(num_auto_parks):
        auto_park = AutoPark.objects.create(slug=fake.slug())
        create_cars(auto_park, num_cars_per_auto_park)
        create_rents(auto_park)


def create_cars(auto_park, num_cars=10):
    car_data = [
        {"brand": "Toyota", "model": "Camry"},
        {"brand": "Honda", "model": "Accord"},
        {"brand": "Ford", "model": "F-150"},
        {"brand": "BMW", "model": "3 Series"},
        {"brand": "Mercedes-Benz", "model": "C-Class"},
        {"brand": "Audi", "model": "A4"},
        {"brand": "Volkswagen", "model": "Golf"},
        {"brand": "Chevrolet", "model": "Silverado"},
        {"brand": "Nissan", "model": "Altima"},
        {"brand": "Hyundai", "model": "Elantra"}
    ]

    car_types = ["Sedan", "SUV", "Hatchback", "Coupe", "Convertible", "Minivan", "Pickup Truck"]

    for _ in range(num_cars):
        car_data_entry = random.choice(car_data)
        brand_title = car_data_entry["brand"]
        model_title = car_data_entry["model"]

        car_brand, _ = CarBrand.objects.get_or_create(title=brand_title)
        car_type, _ = CarType.objects.get_or_create(title=random.choice(car_types))

        car = Car.objects.create(
            year=random.randint(1990, timezone.now().year),
            price_per_day=random.randint(20, 200),
            name=model_title,
            car_brand=car_brand,
            car_type=car_type
        )

        AutoParkCar.objects.create(auto_park=auto_park, car=car, is_rented=False)


def create_rents(auto_park, num_rents=20):
    cars = AutoParkCar.objects.filter(auto_park=auto_park, is_rented=False)
    users = CustomUser.objects.all()

    if not cars.exists():
        print(f"No available cars to rent for auto park: {auto_park.slug}")
        return

    if not users.exists():
        print("No users available to rent cars.")
        return

    for _ in range(min(num_rents, cars.count())):
        auto_park_car = random.choice(cars)
        car = auto_park_car.car
        user = random.choice(users)
        rental_date = timezone.now()
        expected_return_date = rental_date + timezone.timedelta(days=random.randint(1, 7))

        Rent.objects.create(
            user=user,
            car=car,
            auto_park=auto_park,
            rental_date=rental_date,
            expected_return_date=expected_return_date
        )

        auto_park_car.is_rented = True
        auto_park_car.save()


create_auto_parks_with_cars()
