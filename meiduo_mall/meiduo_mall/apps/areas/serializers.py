from rest_framework import serializers

from .models import Area


class AreasSerializer(serializers.ModelSerializer):
    """序列化省数据"""

    class Meta:
        model = Area
        fields = ['id', 'name']


class SubsAreasSerializer(serializers.ModelSerializer):
    """序列化市和区的数据"""
    subs = AreasSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']
