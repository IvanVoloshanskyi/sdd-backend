from django.db import models


class Car(models.Model):
    year = models.PositiveSmallIntegerField(default=1990)
    price_per_day = models.IntegerField(default=0)
    name = models.CharField(max_length=50)
    car_brand = models.ForeignKey('CarBrand', on_delete=models.CASCADE)
    car_type = models.ForeignKey('CarType', on_delete=models.CASCADE)
    penalty_amount = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.car_brand} / {self.name} / {self.car_type}'


class CarBrand(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class CarType(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title
