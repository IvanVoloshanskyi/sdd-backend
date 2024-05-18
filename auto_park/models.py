from django.db import models

from auto_park.car_model import Car


class AutoPark(models.Model):
    slug = models.SlugField(unique=True)
    cars = models.ManyToManyField(Car, blank=True)

    def __str__(self):
        return f'{self.slug} / {self.cars.count()} cars in park'
