import json
from rest_framework import serializers
from .models import Route, Stop, Bus, StaffUser

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id','name', 'time']

class RouteSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True)

    class Meta:
        model = Route
        fields = ['id','name', 'stops']

    def create(self, validated_data):
        stops_data = validated_data.pop('stops')
        route = Route.objects.create(**validated_data)
        for stop_data in stops_data:
            Stop.objects.create(route=route, **stop_data)
        return route
    
class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['id','bus_image', 'bus_number','bus_capacity','driver_name','operator_name','bus_route','alternate_route']

    def create(self, validated_data):
        return super().create(validated_data)

class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffUser
        fields = ['id', 'first_name', 'last_name']

class BusListSerializer(serializers.ModelSerializer):
    driver_name = StaffUserSerializer(read_only=True)
    operator_name = StaffUserSerializer(read_only=True)
    bus_route = RouteSerializer(read_only=True)
    alternate_route = RouteSerializer(read_only=True)

    class Meta:
        model = Bus
        fields = ['id','driver_name','operator_name','bus_route','alternate_route','bus_image','bus_number','bus_capacity']