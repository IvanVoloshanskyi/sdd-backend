from rest_framework import serializers

from auto_park.models import Car


class CarfleetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
