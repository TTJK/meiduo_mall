from django.shortcuts import render
from rest_framework.generics import CreateAPIView
# Create your views here.
from . import serializers
from rest_framework.views import APIView
from .models import User
from rest_framework.response import Response

class UserView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer

class UsernameCountView(APIView):
    def get(self,request,username):
        count = User.objects.filter(username=username).count()

        data = {
            'username':username,
            'count':count
            }
        return Response(data)

class MobileCountView(APIView):
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile':mobile,
            'count':count
            }
        return Response(data)