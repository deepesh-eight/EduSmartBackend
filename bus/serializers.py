import json
from rest_framework import serializers

from EduSmart import settings
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


class BusDetailSerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField()
    driver_id = serializers.SerializerMethodField()
    driver_no = serializers.SerializerMethodField()
    driver_gender = serializers.SerializerMethodField()
    operator_id = serializers.SerializerMethodField()
    operator_name = serializers.SerializerMethodField()
    operator_gender = serializers.SerializerMethodField()
    operator_no = serializers.SerializerMethodField()
    operator_email = serializers.SerializerMethodField()
    bus_image = serializers.SerializerMethodField()
    bus_route_name = serializers.SerializerMethodField()
    main_route = serializers.SerializerMethodField()
    alternate_route_name = serializers.SerializerMethodField()
    class Meta:
        model = Bus
        fields = ['id', 'driver_name', 'driver_id', 'driver_gender', 'driver_no', 'operator_id', 'operator_name', 'operator_gender', 'operator_no', 'operator_email', 'bus_image', 'bus_number', 'bus_capacity', 'bus_route', 'bus_route_name', 'main_route', 'alternate_route', 'alternate_route_name']

    def get_driver_id(self, obj):
        driver_id = StaffUser.objects.get(id=obj.driver_name.id)
        if driver_id:
            return driver_id.id
        else:
            None

    def get_driver_name(self, obj):
        driver_name = StaffUser.objects.get(id=obj.driver_name.id)
        if driver_name:
            return f"{driver_name.first_name} {driver_name.last_name}"
        else:
            None

    def get_driver_no(self, obj):
        driver_no = StaffUser.objects.get(id=obj.driver_name.id)
        if driver_no:
            return str(driver_no.user.phone)
        else:
            None

    def get_driver_gender(self, obj):
        driver_gender = StaffUser.objects.get(id=obj.driver_name.id)
        if driver_gender:
            return driver_gender.gender
        else:
            None

    def get_operator_id(self, obj):
        operator_id = StaffUser.objects.get(id=obj.operator_name.id)
        if operator_id:
            return operator_id.id
        else:
            None

    def get_operator_name(self, obj):
        operator_name = StaffUser.objects.get(id=obj.operator_name.id)
        if operator_name:
            return f"{operator_name.first_name} {operator_name.last_name}"
        else:
            None

    def get_operator_no(self, obj):
        operator_no = StaffUser.objects.get(id=obj.driver_name.id)
        if operator_no:
            return str(operator_no.user.phone)
        else:
            None

    def get_operator_email(self, obj):
        operator_email = StaffUser.objects.get(id=obj.driver_name.id)
        if operator_email:
            return operator_email.user.email
        else:
            None

    def get_operator_gender(self, obj):
        operator_gender = StaffUser.objects.get(id=obj.driver_name.id)
        if operator_gender:
            return operator_gender.gender
        else:
            None

    def get_bus_image(self, obj):
        if obj.bus_image:
            if obj.bus_image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.bus_image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.bus_image)}'
        return None

    def get_bus_route_name(self, obj):
        route = Route.objects.get(id=obj.bus_route.id)
        stops = Stop.objects.filter(route=route)
        stop_name = []
        for stop in stops:
            stop_name.append(stop.name)
        return stop_name

    def get_alternate_route_name(self, obj):
        route = Route.objects.get(id=obj.alternate_route.id)
        stops = Stop.objects.filter(route=route)
        stop_name = []
        for stop in stops:
            stop_name.append(stop.name)
        return stop_name

    def get_main_route(self, obj):
        route = Route.objects.get(id=obj.bus_route.id)
        return route.name


class RouteListSerializer(serializers.ModelSerializer):
    stop_name = serializers.SerializerMethodField()
    stop_time = serializers.SerializerMethodField()
    stop = serializers.SerializerMethodField()
    class Meta:
        model = Route
        fields = ['id','name', 'stop_name', 'stop_time', 'stop']

    def get_stop_name(self, obj):
        stop = Stop.objects.filter(route=obj)
        stops_name = []
        if stop:
            for stop_name in stop:
                stops_name.append(stop_name.name)
            return stops_name
        else:
            None

    def get_stop_time(self, obj):
        stop = Stop.objects.filter(route=obj)
        stops_time = []
        if stop:
            for stop_name in stop:
                stops_time.append(stop_name.time.strftime("%I:%M %p"))
            return stops_time
        else:
            None

    def get_stop(self, obj):
        stops = Stop.objects.filter(route=obj)
        stop_list = []
        for stop in stops:
            stop_data = {
                "stop_name": stop.name,
                "stop_time": stop.time.strftime("%I:%M %p")
            }
            stop_list.append(stop_data)
        return stop_list


class BusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['id', 'bus_image', 'bus_number', 'bus_capacity', 'driver_name', 'operator_name', 'bus_route', 'alternate_route', 'bus_capacity']


class StopUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id','name', 'time']


class RouteUpdateSerializer(serializers.ModelSerializer):
    stops = StopUpdateSerializer(many=True)

    class Meta:
        model = Route
        fields = ['id','name', 'stops']

    def update(self, instance, validated_data):
        stops_data = validated_data.pop('stops')
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        instance.stops.all().delete()

        for stop_data in stops_data:
            Stop.objects.create(route=instance, **stop_data)

        return instance
