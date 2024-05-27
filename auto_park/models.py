from django.db import models

from auto_park.car_model import Car


class AutoPark(models.Model):
    slug = models.SlugField(unique=True)
    cars = models.ManyToManyField('Car', through='AutoParkCar', blank=True)

    def __str__(self):
        return f'{self.slug} / {self.cars.count()} cars in park'


class AutoParkCar(models.Model):
    auto_park = models.ForeignKey(AutoPark, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    is_rented = models.BooleanField(default=False)

